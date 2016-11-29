# coding: utf-8
import sys
sys.path.append(r"D:\virtualenv\caipiao\venv\lib\site-packages")

import scrapy
from v1.items import V1Item
from v1.helper import get_crawl_list, get_detail_list, get_url_list
from scrapy import Request

class Spider1(scrapy.spiders.Spider):
    name = 'v1'


    def __init__(self, category=None, *args, **kwargs):
        super(Spider1, self).__init__(*args, **kwargs)
        self.crawl_list = get_crawl_list(category)
        self.start_urls = self.crawl_list


    def start_requests(self):
        for each in self.start_urls:
            yield self.make_requests_from_url(each)

    def make_requests_from_url(self, each):
        return Request(each.get('website'), dont_filter=True, meta=each)

    def parse(self,response):
        url_list = get_url_list(response)
        for i in url_list:
            yield Request(i, callback=self.parse_info, meta=response.meta)

    def parse_info(self,response):
        item = V1Item()
        if response.meta.get('other_response') == 'json':
            import re
            import json
            sel = json.loads(response.body)
            item['balance'] = eval(response.meta.get('balance'))
            item['name'] = response.meta.get('name')
            item['issue'] = eval(response.meta.get('issue'))
            item['key'] = response.meta.get('key')
            item['open_time'] = eval(response.meta.get('open_time'))
            item['result'] = eval(response.meta.get('result'))
            item['sales'] = eval(response.meta.get('sales'))
            item['src'] = response.meta.get('src')

            # item['balance'] = re.findall(response.meta.get('balance'),response.body)[0] if response.meta.get('balance') else None
            # item['name'] = response.meta.get('name')
            # item['issue'] = re.findall(response.meta.get('issue'),response.body)[0] if response.meta.get('issue') else None
            # item['key'] = response.meta.get('key')
            # item['open_time'] = re.findall(response.meta.get('open_time'),response.body)[0] if response.meta.get('open_time') else None
            # item['result'] = re.findall(response.meta.get('result'),response.body)[0] if response.meta.get('result') else None
            # item['sales'] = re.findall(response.meta.get('sales'),response.body)[0] if response.meta.get('sales') else None
            # item['src'] = response.meta.get('src')
            detail_list = get_detail_list(sel,response) if response.meta.get('detail') else ''
            item['detail'] = detail_list
            yield item
        else:
            sel = response.selector
            for i in ['balance','issue','open_time','sales']:
                if response.meta.get(i):
                    query = response.meta.get(i)
                    if isinstance(query, dict):
                        item[i] = sel.xpath(query.get('xpath')).xpath('string(.)').extract()[0]
                        from re import findall
                        item[i] = findall(query.get('regex'), item[i])[0] if findall(query.get('regex'), item[i]) else item[i]
                    else:
                        item[i] = sel.xpath(query + '/text()').extract()[0]
                else:
                    item[i] = ''
            if len(sel.xpath(response.meta.get('result'))) == 1:
                item['result'] = sel.xpath(response.meta.get('result')).extract()
            else:
                item['result'] = sel.xpath(response.meta.get('result') + '/text()').extract()
                item['result'] = ','.join(item['result'])

            item['name'] = response.meta.get('name')
            item['key'] = response.meta.get('key')
            item['src'] = response.meta.get('src')

            detail_list = get_detail_list(sel, response) if response.meta.get('detail') else None
            item['detail'] = detail_list
            yield item






