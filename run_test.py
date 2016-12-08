#coding:utf-8
from twisted.internet import reactor,defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from v1.spiders.spider1 import Spider1
from lottery import is_cron
# import pymongo
# from scrapy.conf import settings
from datetime import datetime
import os
import json
#from json
json_location = os.path.dirname(os.path.abspath(__file__)) + r'/v1/spiders/query.json'
print json_location

# host = settings['MONGO_HOST']
# port = settings['MONGO_PORT']
# dbName = settings['MONGO_DBNAME']
# collection_name = settings['MONGO_QUERY']
# client = pymongo.MongoClient(host=host,port=port)
# db = client[dbName]
# collection = db[collection_name]

def div_list(ls,n=3):
    alist = []
    if len(ls) < n:
        alist.append(ls)
        return alist
    elif len(ls) == 3:
        for i in ls:
            alist.append([i])
        return alist
    else:
        j = len(ls)%n
        k = len(ls)/n
        for i in range(k):
            alist.append(ls[i*n:i*n + n])
        if j:
            alist.append(ls[k*n:])
        return alist
def start():
    start_urls = []
    s = datetime.utcnow()
    print s
    #from json
    with open(json_location, 'r') as f:
        query = json.load(f)

    for i in query:
        start_urls.append(i)
    # for i in collection.find({}):
    #     crontab = i.get('crontab')
    #     print crontab
    #     if crontab:
    #         print is_cron(s, crontab)
    #         if is_cron(s,crontab):
    #             start_urls.append(i)
    if not start_urls:
        print 'no start_urls'
    return start_urls


if __name__ == '__main__':
    if start():
        start_urls = start()

        # for i in collection.find({}):
        #     start_urls.append(i)

        runner = CrawlerRunner(get_project_settings())
        dfs = set()
        for i in div_list(start_urls):
            d = runner.crawl(Spider1, start_urls=i)
            # runner.crawl(Spider1, start_urls=i)
            dfs.add(d)

        # d = runner.join
        # d.addBoth(lambda _: reactor.stop())

        defer.DeferredList(dfs).addBoth(lambda _: reactor.stop())
        reactor.run()