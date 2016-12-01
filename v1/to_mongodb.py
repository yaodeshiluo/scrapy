import pymongo
import json

# with open(r'D:\virtualenv\caipiao\v1\v1\spiders\query.json') as f:
#     querys = json.load(f)

client = pymongo.MongoClient(host='127.0.0.1',port=27017)
db = client.caipiao
collection = db.query
# for each in querys:
#     collection.insert(dict(each))

collection.update({"_id":{"$exists":True}},{"$set":{"crontab":['*/2 * * * *']}},multi=True)



from v1.lottery import is_cron
import datetime
s = datetime.datetime.utcnow()
print s
print is_cron(s,'00 */2 * * *')


import json
querys = collection.find({"caizhong":"fucai3d"})
alist = list()
for i in querys:
    alist.append(i)
print alist
print alist[0].get('ObjectId')
print alist[0].pop('_id')

print json.dumps(alist)
with open('test.json','w') as f:
    f.write(json.dumps(alist))