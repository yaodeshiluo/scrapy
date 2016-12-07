# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
import pymongo
from datetime import datetime
from pipeline_helper import different, str2num, to_server


class MongoPipeline(object):
    def __init__(self):
        self.host = settings['MONGO_HOST']
        self.port = settings['MONGO_PORT']
        self.dbName = settings['MONGO_DBNAME']
        self.collection_name = settings['MONGO_DOCNAME']

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(host=self.host,port=self.port)
        db = self.client[self.dbName]
        self.collection = db[self.collection_name]

    def close_spider(self,spider):
        self.client.close()

    def process_item(self, item, spider):
        # self.collection.insert(dict(item))
        # print item
        mongo_item = self.collection.find({"key":item.get('key'),"src":item.get('src'),"issue":item.get('issue')})
        if mongo_item.count():
            print 'updating'
            for i in mongo_item:
                if different(i,item):
                    print item
                    to_server(item)
                    difference = different(i,item)
                    difference['status'] = item.get('status')
                    difference['update_time'] = datetime.utcnow()
                    self.collection.update({'_id':i.get('_id')},{'$set':difference})
                    print 'updated'
        else:
            print 'inserting'
            print item
            to_server(item)
            # try:
            #     to_server(item)
            # except:
            #     import traceback
            #     print traceback.format_exc()
            item['create_time'] = datetime.utcnow()
            self.collection.insert(dict(item))
            print 'inserted'

        return item


class StripPipeline(object):
    def process_item(self, item, spider):
        for field in item.fields:
            if item.get(field):
                if isinstance(item.get(field), basestring):
                    item[field] = item[field].strip()
                #detail strip()
                elif isinstance(item.get(field), list):
                    alist = item.get(field)
                    for i in alist:
                        if isinstance(i,dict):
                            for k,v in i.iteritems():
                                if isinstance(v, basestring):
                                    i[k] = v.strip()
        return item


class Str2intPipeline(object):
    def process_item(self, item, spider):
        for key in ['balance','sales']:
            if item.get(key):
                item[key] = str2num(item.get(key))
            else:
                item[key] = 0
        return item


