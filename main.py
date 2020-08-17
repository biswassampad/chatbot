import sqlite3
import json
from datetime import datetime


from model import addDataToDb


timeframe = "2005-12"

sql_transaction = []

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS parent_reply(parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT, comment TEXT, subreddit TEXT, unix INT, score INT)")

def format_data(data):
    data = data.replace('\n',' newlinechar ').replace('\r',' newlinechar ').replace('"',"'")
    return data

def transaction_bldr(sql):
    global sql_transaction
    sql_transaction.append(sql)
    if len(sql_transaction) > 1000:
        c.execute('BEGIN TRANSACTION')
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()
        sql_transaction = []

def sql_insert_replace_comment(commentid,parentid,parent,comment,subreddit,time,score):
    print('inserting to replace comment')
    data = {
        'commentid': commentid,
        'parentid':parentid,
        'parent':parentid,
        'comment':comment,
        'subreddit':subreddit,
        'time':time,
        'score':score
    }
    execute = addDataToDb().insert_type_one(data)
    print(execute)

def sql_insert_has_parent(commentid,parentid,parent,comment,subreddit,time,score):
    print('inserting to has parent')
    data = {
        'commentid': commentid,
        'parentid':parentid,
        'parent':parentid,
        'comment':comment,
        'subreddit':subreddit,
        'time':time,
        'score':score
    }
    execute = addDataToDb().insert_type_one(data)
    print(execute)
    

def sql_insert_no_parent(commentid,parentid,comment,subreddit,time,score):
    print('inserting to has no parent')
    data = {
        'commentid': commentid,
        'parentid':parentid,
        'parent':parentid,
        'comment':comment,
        'subreddit':subreddit,
        'time':time,
        'score':score
    }
    execute = addDataToDb().insert_type_one(data)
    print(execute)
  

def acceptable(data):
    if len(data.split(' ')) > 50 or len(data) < 1:
        return False
    elif len(data) > 1000:
        return False
    elif data == '[deleted]':
        return False
    elif data == '[removed]':
        return False
    else:
        return True

def find_parent(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    except Exception as e:
        print(str(e))
        return False

def find_existing_score(pid):
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    except Exception as e:
        print(str(e))
        return False



if __name__ == "__main__":
    create_table()
    row_counter = 0
    paired_rows = 0 

    with open("one" ,buffering=1000) as f:
        for row in f:
            row_counter += 1
            row = json.loads(row)
            comment_id = row['id']
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']

            parent_data = find_parent(parent_id)

            if score >= 2:
                if acceptable(body):
                    existing_comment_score = find_existing_score(parent_id)
                    if existing_comment_score:
                        if score >existing_comment_score:
                            sql_insert_replace_comment(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)
                    else:
                        if parent_data:
                            sql_insert_has_parent(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)
                        else:
                            sql_insert_no_parent(comment_id,parent_id,body,subreddit,created_utc,score)
            # print('Total rows read: {}, Paired rows: {},Time:{}'.format(row_counter,paired_rows,str(datetime.now())))

            if row_counter % 100000 == 0:
                print('Total rows read: {}, Paired rows: {},Time:{}'.format(row_counter,paired_rows,str(datetime.now())))