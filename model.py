import pymongo
import json

from db_config import connect_db

class addDataToDb():
    def insert_type_one(self,data):
        try:
            dumped = json.dumps(data)
            prem = json.loads(dumped)
            process = connect_db().comments.insert_one(prem)
            print(process)
            print('Data Insertion successfull')
            return True
        except Exception as e:
            print('error {}'.format(e))
