import pymongo
import os

def connect_db():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["chatbot"]
    return mydb