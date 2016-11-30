# coding: utf-8
import sys
sys.path.append(r"D:\virtualenv\caipiao\venv\lib\site-packages")

import scrapy
from v1.items import V1Item
from v1.helper import get_crawl_list, get_detail_list, get_url_list, parse_single_item_from_json
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
            if response.meta.get('json_info').get('regex'):
                json_query = response.meta.get('json_info').get('regex')
                try:
                    target_json = json.loads(re.findall(json_query,response.body)[0])
                except:
                    target_json = json.loads(re.findall(json_query, response.body)[0] + '}')
            else:
                target_json = json.loads(response.body)

            if response.meta.get('json_info').get('how_many_items') == 'single':
                sel = target_json
                item = parse_single_item_from_json(item,response,sel)
                # item['balance'] = eval(response.meta.get('balance'))
                # item['name'] = response.meta.get('name')
                # item['issue'] = eval(response.meta.get('issue'))
                # item['key'] = response.meta.get('key')
                # item['open_time'] = eval(response.meta.get('open_time'))
                # item['result'] = eval(response.meta.get('result'))
                # item['sales'] = eval(response.meta.get('sales'))
                # item['src'] = response.meta.get('src')

                # detail_list = get_detail_list(sel,response) if response.meta.get('detail') else ''
                # item['detail'] = detail_list
                yield item
            elif response.meta.get('json_info').get('how_many_items') == 'many':
                if isinstance(target_json,dict):
                    for sel in target_json.iteritems():
                        item = parse_single_item_from_json(item,response,sel)
                        yield item
                if isinstance(target_json,list):
                    for sel in target_json:
                        item = parse_single_item_from_json(item,response,sel)
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
    def parse_all_in_one(self,response):
        sel = response.selector
        tr_list = []
        if isinstance(response.meta.get('items_table'), basestring):
            useless_rows = response.meta.get('useless_rows') if response.meta.get('useless_rows') else []
            append = None
            for tr_num, tr in enumerate(sel.xpath(response.meta.get('items_table') + '//tr')):
                if tr_num in useless_rows:
                    pass
                else:
                    each_tr = []
                    if append:
                        each_tr.append(append)
                        append = None
                    for td_num, each_td in enumerate(tr.xpath('*')):
                        if each_td.xpath('@colspan'):
                            for i in range(int(each_td.xpath('@colspan').extract()[0])):
                                each_tr.append(each_td.xpath('string(.)').extract()[0])
                        else:
                            each_tr.append(each_td.xpath('string(.)').extract()[0])
                        if each_td.xpath('@rowspan'):
                            append = each_td.xpath('string(.)').extract()[0]

                    tr_list.append(each_tr)



        if response.meta.get('tr_0'):
            tr_list.insert(0, response.meta.get('tr_0'))

        # filter. list like['','',''] will be removed from tr_list
        tr_list = filter(lambda x: filter(lambda y: y, x), tr_list)
        print 'tr_list is', tr_list

        detail_list = []
        tr_0 = tr_list[0]
        for num in range(1, len(tr_list)):
            each_tr = tr_list[num]
            adict = {}

            # adict[tr_0[0]] = each_tr[0]
            # for i in range(1, len(each_tr)):
            #     if tr_0[i] == tr_0[i - 1]:
            #         if each_tr[i] != adict[tr_0[i - 1]]:
            #             adict[tr_0[i]] += each_tr[i]
            #         else:
            #             pass
            #     else:
            #         adict[tr_0[i]] = each_tr[i]
            detail_list.append(adict)




