#coding:utf-8
from twisted.internet import reactor,defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from v1.spiders.spider1 import Spider1
from lottery import is_cron
import time
import pymongo
from scrapy.conf import settings
from datetime import datetime


host = settings['MONGO_HOST']
port = settings['MONGO_PORT']
dbName = settings['MONGO_DBNAME']
collection_name = settings['MONGO_QUERY']
client = pymongo.MongoClient(host=host,port=port)
db = client[dbName]
collection = db[collection_name]

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
    for i in collection.find({}):
        crontab = i.get('crontab')
        print crontab
        if crontab:
            print is_cron(s, crontab)
            if is_cron(s,crontab):
                start_urls.append(i)
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
            dfs.add(d)

        defer.DeferredList(dfs).addBoth(lambda _: reactor.stop())
        reactor.run()






























    # while True:
    #     print 'start'
    #
    #     start_urls = []
    #     if collection.find({"website": "http://www.lecai.com/lottery/draw/list/52"}).count():
    #         for i in collection.find({}):
    #             crontab = i.get('crontab')
    #             print crontab
    #             s = datetime.utcnow()
    #             print s
    #             # if crontab:
    #             #     print is_cron(s, crontab)
    #             #     if is_cron(s, crontab):
    #             start_urls.append(i)
    #         if start_urls:
    #             print start_urls
    #             runner = CrawlerRunner(get_project_settings())
    #             d =runner.crawl(Spider1, start_urls=start_urls)
    #             d.addBoth(lambda _: reactor.stop())
    #             reactor.run() # the script will block here until the crawling is finished
    #         print 'end'
