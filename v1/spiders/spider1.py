# coding: utf-8
import sys
sys.path.append(r"D:\virtualenv\caipiao\venv\lib\site-packages")
from selenium import webdriver
import scrapy
from v1.items import V1Item
import json
from v1.helper import get_crawl_list, get_detail_list, get_url_list
from scrapy import Request
from scrapy.http import HtmlResponse

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
        # if not response.meta.get('webdriver'):
        # if True:
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
        item = V1Item()
        if response.meta.get('other_response') == 'json':
            # print 'the response type is',type(response)
            # item['name'] = response.body
            import re
            import json
            item['balance'] = re.findall(response.meta.get('balance'),response.body)[0] if response.meta.get('balance') else None
            item['name'] = response.meta.get('name')
            item['issue'] = re.findall(response.meta.get('issue'),response.body)[0] if response.meta.get('issue') else None
            item['key'] = response.meta.get('key')
            item['open_time'] = re.findall(response.meta.get('open_time'),response.body)[0] if response.meta.get('open_time') else None
            item['result'] = re.findall(response.meta.get('result'),response.body)[0] if response.meta.get('result') else None
            item['sales'] = re.findall(response.meta.get('sales'),response.body)[0] if response.meta.get('sales') else None
            item['src'] = response.meta.get('src')
            detail_list = re.findall(response.meta.get('detail'),response.body)[0] if response.meta.get('detail') else None
            item['detail'] = json.loads(detail_list)
            yield item
        else:
            # print 'response.meta is',response.meta
            sel = response.selector
            # elif response.meta.get('webdriver') == 'phantomjs':
            #     meta = response.meta
            #     driver = webdriver.PhantomJS(executable_path=r'D:\Program Files\phantomjs\bin\phantomjs.exe')
            #     driver.get(response.url)
            #     html = driver.page_source
            #     driver.quit()
            #     request = Request(response.url,meta=response.meta)
            #     response = HtmlResponse(url=response.url, encoding='utf-8',body=html, request=request)
            #     sel = response.selector
            if response.meta.get('balance'):
                balance_query = response.meta.get('balance')
                if isinstance(balance_query,dict):
                    from re import findall
                    item['balance'] = findall(balance_query.get('regex'),response.body)[0]
                else:
                    item['balance'] = sel.xpath(balance_query + '/text()').extract()[0]
            else:
                item['balance'] = None
            item['name'] = response.meta.get('name')
            item['issue'] = sel.xpath(response.meta.get('issue') + '/text()').extract()[0]
            item['key'] = response.meta.get('key')
            item['open_time'] = sel.xpath(response.meta.get('open_time') + '/text()').extract()[-1]
            if len(sel.xpath(response.meta.get('result'))) == 1:
                item['result'] = sel.xpath(response.meta.get('result')).extract()
            else:
                item['result'] = sel.xpath(response.meta.get('result') + '/text()').extract()
            item['sales'] = sel.xpath(response.meta.get('sales') + '/text()').extract()[0]
            item['src'] = response.meta.get('src')

            detail_list = get_detail_list(sel, response) if response.meta.get('detail') else None
            item['detail'] = detail_list
            yield item


#test http://www.zhcw.com/kj/qg/wqcx/
# import sys
# sys.path.append(r"D:\virtualenv\caipiao\venv\lib\site-packages")
# sys.path.append(r"D:\virtualenv\caipiao\v1\v1")
# from selenium import webdriver
# import scrapy
# # from v1.items import V1Item
# import time
# import json
# from helper import get_crawl_list, get_detail_list, get_url_list
# from scrapy import Request
# from scrapy.http import HtmlResponse
# driver = webdriver.PhantomJS(executable_path=r'D:\Program Files\phantomjs\bin\phantomjs.exe')
# driver.get("http://www.lecai.com/lottery/draw/list/50")
# # time.sleep(5)
# html = driver.page_source
# driver.quit()
# request = Request("http://www.lecai.com/lottery/draw/list/50", meta={"urllist":"//table[@class='historylist']/tbody/tr[position()>=1 and position()<=30]/td[1]/a/@href"})
# response = HtmlResponse(url="http://www.lecai.com/lottery/draw/list/50", encoding='utf-8', body=html, request=request)
# url_list = get_url_list(response)
# print url_list





