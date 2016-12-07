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
        # self.crawl_list = get_crawl_list(category)
        # self.start_urls = self.crawl_list


    def start_requests(self):
        for each in self.start_urls:
            yield self.make_requests_from_url(each)

    def make_requests_from_url(self, each):
        return Request(each.get('website'), dont_filter=True, meta=each)

    def parse(self,response):
        if not response.meta.get('urllist'):
            yield Request(response.meta.get('website'), callback=self.parse_all_in_one, meta=response.meta)
        else:
            url_list = get_url_list(response)
            for i in url_list:
                yield Request(i, callback=self.parse_info, meta=response.meta)

    def parse_info(self,response):
        item = V1Item()
        if response.meta.get('other_response') == 'json':
            '''
            meta里需含有以下key：
            other_response,
            json_info:{regex/how_many_items} 有regex则从response.body正则提取json
            detail:[]  basestring直接eval  dict含regex（直接从response.body提取）；含input，直接手输，优先。
            tr_0:[]
            '''
            import re
            import json
            #有other_response就必须有json_info，不然报错
            if response.meta.get('json_info').get('regex'):
                #target_json有从response得到的，也有通过regex从response.body里取得。
                json_query = response.meta.get('json_info').get('regex')
                try:
                    target_json = json.loads(re.findall(json_query,response.body)[0])
                except:
                    target_json = json.loads(re.findall(json_query, response.body)[0] + '}')
            else:
                target_json = json.loads(response.body)
            #json_info必须有两个key，一个是regex，一个是how_many_items
            if response.meta.get('json_info').get('how_many_items') == 'single':
                sel = target_json
                item = parse_single_item_from_json(item,response,sel)
                yield item
            elif response.meta.get('json_info').get('how_many_items') == 'many':
                #target_json含多个item信息时，需迭代。其可能为dict，也可能为list，对应不同迭代方式。
                if isinstance(target_json,dict):
                    for sel in target_json.iteritems():
                        item = parse_single_item_from_json(item,response,sel)
                        yield item
                if isinstance(target_json,list):
                    for sel in target_json:
                        item = parse_single_item_from_json(item,response,sel)
                        yield item
        else:#最常见的解析页面。即有table和其他信息。
            sel = response.selector
            #以下每个key都有regex和xpath两种解析方式
            '''
            meta里需含有以下key：
            首先不含other_response（或为空）,
            detail:[]  basestring直接xpath得到表格，再常规解析表格。
                       若为list，则：
                           对应td若为dict必须xpath和input必有其中一项。
                           若有regex则会进一步对xpath得到的值再取值。
            tr_0:[]
            '''
            for i in ['balance','issue','open_time','sales']:
                if response.meta.get(i):
                    query = response.meta.get(i)
                    #直接先xpath里的值extract后（可能包括<div>等元素符号）用regex
                    if isinstance(query, dict):
                        item[i] = sel.xpath(query.get('xpath')).extract()[0]
                        from re import findall
                        item[i] = findall(query.get('regex'), item[i])[0] \
                            if findall(query.get('regex'), item[i]) else item[i]
                    else:
                        if sel.xpath(query + '/text()').extract():
                            item[i] = sel.xpath(query + '/text()').extract()[0]
                        else:
                            item[i] = sel.xpath(query).extract()[0] \
                                if sel.xpath(query).extract() else ''
                else:
                    item[i] = ''
            #result列表和字符串两种形式的结果的处理。
            #result 目前直接xpath得到。暂无需要regex的情况
            if sel.xpath(response.meta.get('result') + '/text()'):
                item['result'] = sel.xpath(response.meta.get('result')).xpath('string(.)').extract()
            else:
                item['result'] = sel.xpath(response.meta.get('result')).extract()
            item['result'] = ','.join(item['result'])

            # if len(sel.xpath(response.meta.get('result'))) == 1:
            #     item['result'] = sel.xpath(response.meta.get('result')).extract()[0]
            # else:
            #     item['result'] = sel.xpath(response.meta.get('result') + '/text()').extract()
            #     item['result'] = ','.join(item['result'])


            item['name'] = response.meta.get('name')
            item['key'] = response.meta.get('key')
            item['src'] = response.meta.get('src')
            item['url'] = response.url


            #相关的meta信息有useless_rows，tr_0,且无other_response这一项。
            detail_list = get_detail_list(sel, response) if response.meta.get('detail') else ''
            item['detail'] = detail_list
            yield item
    '''
    上面两处方法都是先得到urllist，再从每个url返回的页面提取单个item的信息。
    下面这个方法则是从一个页面得到多个item。
    所以meta里的urllist为空。parse这一函数会将请求callback设置为parse_all_in_one。
    meta里需有的key：
    tr_0    设置比较特殊。是list，非item里detail的诸如sales,open_time等直接手输，对应表格相应位置。
            但detail里的键如name，count，money，则[{"name":"一等奖"},"count"],[{"name":"一等奖"},"money"]
    items_table 包含items的表格的xpath
    '''
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
        # print 'tr_list is', tr_list

        tr_0 = tr_list[0]

        for num in range(1, len(tr_list)):
            each_tr = tr_list[num]
            tem_dict = None
            target_dict = None
            adict = {}
            detail_list = []

            adict[tr_0[0]] = each_tr[0]
            for i in range(1, len(each_tr)):
                if isinstance(tr_0[i], basestring):
                    if tr_0[i] == tr_0[i - 1]:
                        if each_tr[i] != adict[tr_0[i - 1]]:
                            adict[tr_0[i]] += each_tr[i]
                        else:
                            pass
                    else:
                        adict[tr_0[i]] = each_tr[i]
                elif isinstance(tr_0[i], list):

                    if not tem_dict:
                        tem_dict = tr_0[i][0].copy()
                        target_dict = tr_0[i][0].copy()
                        target_dict[tr_0[i][1]] = each_tr[i]
                    if tem_dict:
                        if tr_0[i][0] == tem_dict:
                            target_dict[tr_0[i][1]] = each_tr[i]
                        if tr_0[i][0] != tem_dict:
                            detail_list.append(target_dict.copy())
                            tem_dict = tr_0[i][0].copy()
                            target_dict = tr_0[i][0].copy()
                            target_dict[tr_0[i][1]] = each_tr[i]
                            # target_dict = tr_0[i][0]

                if i == len(each_tr) - 1:
                    if target_dict:
                        detail_list.append(target_dict)
                        adict["detail"] = detail_list

            item = V1Item()
            item['balance'] = adict.get('balance','')
            item['name'] = response.meta.get('name')
            item['issue'] = adict.get('issue','')
            item['key'] = response.meta.get('key')
            item['open_time'] = adict.get('open_time','')
            item['result'] = adict.get('result','')
            item['sales'] = adict.get('sales','')
            item['src'] = response.meta.get('src')
            item['detail'] = adict.get('detail','')
            item['url'] = response.url


            yield item





