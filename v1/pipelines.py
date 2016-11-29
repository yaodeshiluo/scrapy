# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
import pymongo

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
        self.collection.insert(dict(item))
        return item
