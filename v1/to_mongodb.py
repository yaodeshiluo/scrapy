#coding=utf-8
import pymongo
import json


# with open(r'D:\virtualenv\caipiao\v1\v1\spiders\query.json') as f:
#     querys = json.load(f)

#判断item在mongo里是否存在或是不同
def different(i,item):
    difference = {}
    for key in i.keys():
        if key in ['_id','name','src','issue','update_time','create_time','key','caizhong','website']:
            continue
        if i.get(key) != item.get(key) and item.get(key):
            difference[key] = item.get(key)
    return difference


client = pymongo.MongoClient(host='127.0.0.1',port=27017)
db = client.caipiao
collection = db.test


#update mongo里的query,将
with open(r'D:\virtualenv\caipiao\v1\v1\spiders\query.json','r') as f:
    query = json.load(f)
collection = db.query
for i in query:
    if not i.get('crontab'):
        print 'no crontab'
    collection.update({"name":i.get('name'),'src':i.get('src'),'webdriver':i.get('webdriver')},
                      {'$set':i},upsert=True,multi=True)
print 'upsert',len(query)




#测试update是否正常运行
# import datetime
# item = {u'src': u'www.lecai.com', u'open_time': u'2016-12-02', u'url': u'http://www.lecai.com/lottery/draw/view/51/2016142', u'sales': u'9,913,024', u'detail': [{u'count': u'3', u'money': u'1264303', u'name': u'\u4e00\u7b49\u5956'}, {u'count': u'13', u'money': u'25365', u'name': u'\u4e8c\u7b49\u5956'}, {u'count': u'367', u'money': u'1797', u'name': u'\u4e09\u7b49\u5956'},\
#         {u'count': u'1066', u'money': u'200', u'name': u'\u56db\u7b49\u5956'}, {u'count': u'10839', u'money': u'50', u'name': u'\u4e94\u7b49\u5956'}, {u'count': u'18898',
# u'money': u'10', u'name': u'\u516d\u7b49\u5956'}, {u'count': u'123136', u'money': u'5', u'name': u'\u4e03\u7b49\u5956'}], u'result': u'02,10,12,18,23,28,30,05', u'key': u'qilecai', u'balance': u'0', u'issue': u'2016142', u'name': u'\u4e03\u4e50\u5f69'}
# print 't',collection.find({"src":"www.lecai.com"}).count()
# # for i in collection.find({"name":'七乐彩',"src":'www.lecai.com',"issue":'2016142'}):
# #     print different(i,item)
# mongo_item = collection.find({"name":'七乐彩',"src":'www.lecai.com',"issue":'2016142'})
# print mongo_item.count()
# if mongo_item.count():
#     for i in mongo_item:
#         if different(i, item):
#             difference = different(i, item)
#             print 'difference is',difference
#             difference['update_time'] = datetime.datetime.utcnow()
#             collection.update({'_id': i.get('_id')}, {'$set': difference})
# else:
#     collection.insert(dict(item))

#测试POST提交数据
# mongo_item = collection.find({"name":'七乐彩',"src":'www.lecai.com',"issue":'2016141'})
# print mongo_item
# post = {"data":[]}
# for i in mongo_item:
#     i.pop('_id')
#     if i.get('update_time'):
#         i.pop('update_time')
#     if i.get('create_time'):
#         i.pop('create_time')
#     print i
#     post.get("data").append(i)
# import json
# post = json.dumps(post)
# print type(post)
# # import urllib
# # post_data = urllib.urlencode(post)
# print post
# import urllib2
# requrl = "http://120.26.81.70:8001/input/v1/input/batch"
# req = urllib2.Request(url=requrl,data=post)
# print 'req is',req
# try:
#     response = urllib2.urlopen(req,timeout=5)
#     responsedata = response.read()
#     print 'response is', response
#     print 'responsedata is', type(responsedata)
# except BaseException,e:
#     print 'error is',e
#     s = repr(e)
#     print 's is',type(s)

#同上,测试POST数据
# adict={
#     "src" : "www.lecai.com",
#     "open_time" : "2016-10-24",
#     "url" : "http://www.lecai.com/lottery/draw/view/51/2016125",
#     "detail" : [
#         {
#             "count" : "0",
#             "money" : "0",
#             "name" : "一等奖"
#         },
#         {
#             "count" : "10",
#             "money" : "24911",
#             "name" : "二等奖"
#         },
#         {
#             "count" : "389",
#             "money" : "1280",
#             "name" : "三等奖"
#         },
#         {
#             "count" : "933",
#             "money" : "200",
#             "name" : "四等奖"
#         },
#         {
#             "count" : "13196",
#             "money" : "50",
#             "name" : "五等奖"
#         },
#         {
#             "count" : "17634",
#             "money" : "10",
#             "name" : "六等奖"
#         },
#         {
#             "count" : "143108",
#             "money" : "5",
#             "name" : "七等奖"
#         }
#     ],
#     "sales" : 8631494.0,
#     "result" : "01,05,11,20,25,28,29,21",
#     "key" : "qilecai",
#     "balance" : 5334110.0,
#     "issue" : "2016125",
#     "name" : "七乐彩"
# }
# adict = {'name':'qilecai'}
# from pipeline_helper import to_server
# from items import V1Item
# item = V1Item(**adict)
# mongo_item = collection.find({"name":'七乐彩',"src":'www.lecai.com',"issue":'2016141'})
# print mongo_item
# post = {"data":[]}
# alist = []
# for i in mongo_item:
#     i.pop('_id')
#     if i.get('update_time'):
#         i.pop('update_time')
#     if i.get('create_time'):
#         i.pop('create_time')
#     alist.append(i)
# print 'alist is',alist
# item = alist[0]
# item = to_server(item)
# print 'after sever',type(item),item
# db.toserver.insert(dict(item))












#测试crontab
# print item
# for each in querys:
#     collection.insert(dict(each))
#
# collection.update({"_id":{"$exists":True}},{"$set":{"crontab":['*/2 * * * *']}},multi=True)
#
#
#
# from v1.lottery import is_cron
# import datetime
# s = datetime.datetime.utcnow()
# print s
# print is_cron(s,'00 */2 * * *')


# import json
# querys = collection.find({})
# alist = list()
# for i in querys:
#     i.pop('_id')
#     alist.append(i)
# print alist

# print json.dumps(alist)
# with open('linux.json','w') as f:
#     f.write(json.dumps(alist))

#测试将含亿万的str转为num
# def is_num(s):
#     if s == '.':
#         return True
#     return s.isdigit()
# def str2num(num_str):
#     num = 0
#     if u'亿' in num_str:
#         alist = num_str.split(u'亿')
#         print alist
#         num_x8 = float(filter(is_num, num_str.split(u'亿')[0]))
#         alist.pop(0)
#         num_str = ''.join(alist)
#         num += num_x8 * 10 ** 8
#     if u'万' in num_str:
#         alist = num_str.split(u'万')
#         num_x4 = float(filter(is_num, num_str.split(u'万')[0]))
#         alist.pop(0)
#         print alist
#         num_str = ''.join(alist)
#         print alist,num_str
#         num += num_x4 * 10 ** 4
#     if  num_str and filter(is_num, num_str):
#         print type(num_str)
#         num_x1 = float(filter(is_num, num_str))
#         num +=  num_x1
#     return num
# num_str = u'0'
# print str2num(num_str)
# print type(str2num(num_str))

#测试修改dict
# alist = [{1:"3  ",2:"  3   "}]
# for i in alist:
#     if isinstance(i, dict):
#         for k, v in i.iteritems():
#             if isinstance(v, basestring):
#                 i[k] = v.strip()
# print alist

#取四舍五入
# x = 56.7
# print int(2*x)/2+int(2*x)%2