# coding: utf-8
import scrapy
from v1.items import V1Item
import json
from v1.helper import get_crawl_list, get_detail_list, get_url_list
from scrapy import Request

class Spider1(scrapy.spiders.Spider):
    name = 'v1'


    def __init__(self, category="shuangseqiu", *args, **kwargs):
        super(Spider1, self).__init__(*args, **kwargs)
        self.crawl_list = get_crawl_list(category)
        self.start_urls = self.crawl_list
        self.url_count = 0

    def start_requests(self):
        for each in self.start_urls:
            yield self.make_requests_from_url(each)

    def make_requests_from_url(self, each):
        return Request(each.get('website'), dont_filter=True, meta=each)

    def parse(self,response):
        # print 'crawl_list is',len(self.crawl_list) #test
        # print 'id is', self.id #test
        # print response.meta #test
        # print len(url_list_raw) #test
        # print response.url, type(response.url) #test
        # print response.url is 'http://www.cwl.gov.cn/kjxx/ssq/hmhz/' #test
        url_list = get_url_list(response)
        # print 'url_list is', len(url_list), type(url_list) #test
        # print 'url_list is', url_list #test
        for i in url_list:
            yield Request(i, callback=self.parse_info, meta=response.meta)

    def parse_info(self,response):
        print 'response.meta is',response.meta
        sel = response.selector
        item = V1Item()
        item['balance'] = sel.xpath(response.meta.get('balance') + '/text()').extract()[0]
        item['name'] = response.meta.get('name')
        item['issue'] = sel.xpath(response.meta.get('issue')+'/text()').extract()[0]
        item['key'] = response.meta.get('key')
        item['open_time'] = sel.xpath(response.meta.get('open_time')+'/text()').extract()[0]
        item['result'] = sel.xpath(response.meta.get('result')+'/text()').extract()
        item['sales'] = sel.xpath(response.meta.get('sales')+'/text()').extract()[0]
        item['src'] = response.meta.get('src')

        detail_list = get_detail_list(sel,response)
        item['detail'] = detail_list
        yield item




