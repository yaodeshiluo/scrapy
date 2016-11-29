import pymongo
import json

with open(r'D:\virtualenv\caipiao\v1\v1\spiders\query.json') as f:
    querys = json.load(f)

client = pymongo.MongoClient(host='127.0.0.1',port=27017)
db = client.caipiao
collection = db.query
for each in querys:
    collection.insert(dict(each))

