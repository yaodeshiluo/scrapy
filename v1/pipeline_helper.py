#coding=utf-8
import urllib2
import json
import requests


def different(i,item):
    difference = {}
    for key in i.keys():
        if key in ['_id','name','src','issue','update_time',
                   'create_time','key','caizhong','website','status'
                   ]:
            continue
        if i.get(key) != item.get(key) and (item.get(key) or item.get(key) == 0):
            difference[key] = item.get(key)
    return difference


def is_num(s):
    if s == '.':
        return True
    return s.isdigit()
def str2num(num_str):
    num = 0
    if u'亿' in num_str:
        alist = num_str.split(u'亿')
        num_x8 = float(filter(is_num, num_str.split(u'亿')[0]))
        alist.pop(0)
        num_str = ''.join(alist)
        num += num_x8 * 10 ** 8
    if u'万' in num_str:
        alist = num_str.split(u'万')
        num_x4 = float(filter(is_num, num_str.split(u'万')[0]))
        alist.pop(0)
        num_str = ''.join(alist)
        num += num_x4 * 10 ** 4
    if  num_str and filter(is_num, num_str):
        num_x1 = float(filter(is_num, num_str))
        num +=  num_x1
    num = int(round(num))
    return num


# def to_server(item):
#
#     post = {"data":[dict(item)]}
#
#     post = json.dumps(post)
#     print type(item), item
#     print 'post is',post
#
#
#     requrl = "http://120.26.81.70:8001/input/v1/input/batch"
#     req = urllib2.Request(url=requrl,data=post)
#     try:
#         response = urllib2.urlopen(req,timeout=1)
#         item['status'] = response.read()
#     except BaseException,e:
#         item['status'] = repr(e)
#     return item

def to_server(item):
    url = "http://120.26.81.70:8001/input/v1/input/batch"
    data = {"data":[dict(item)]}
    r = requests.post(url, data=json.dumps(data))
    item['status'] = r.text

