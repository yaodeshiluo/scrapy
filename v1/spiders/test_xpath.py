# coding: utf-8
def func():
    import sys
    sys.path.append(r"D:\virtualenv\caipiao\venv\lib\site-packages")
    sys.path.append(r"D:\virtualenv\caipiao\v1\v1")
    from selenium import webdriver
    import scrapy
    # from v1.items import V1Item
    import time
    import json
    from helper import get_crawl_list, get_detail_list, get_url_list
    from scrapy import Request
    from scrapy.http import HtmlResponse
    meta =   {"caizhong":"fucai3d",
        "website":"http://kaijiang.zhcw.com/lishishuju/jsp/3dInfoList.jsp?czId=2",
        "urllist":"/html/body/div/div[3]/table/tbody/tr[position()<=30 and position()>=1]/td[12]/a/@href",
        "balance":"",
        "issue":"//*[@id='select']/option[1]",
        "key": "fucai3d",
        "name": "福彩3D",
        "open_time": "//*[@id='kjsj']",
        "result": "/html/body/div[3]/div[5]/div[1]/div/div[5]//strong",
        "sales": "//*[@id='sales']",
        "src": "http://www.zhcw.com/",
        "detail": "//table[@class='tYong'][1]",
        "webdriver": "phantomjs"
      }
    driver = webdriver.PhantomJS(executable_path=r'D:\Program Files\phantomjs\bin\phantomjs.exe')
    driver.get("http://www.lecai.com/lottery/draw/list/52")
    html = driver.page_source
    driver.quit()
    request = Request(meta.get('website'), meta=meta)
    response = HtmlResponse(url='www.baidu.com', encoding='utf-8', body=html, request=request)
    sel = response.selector
    # # item ={}
    # item = {}


    urllist = sel.xpath("/html/body/div[7]/div[1]/table/tbody/tr[position()>=1 and position()<=30]/td[1]/a/text()").extract()
    # item['balance'] = sel.xpath(response.meta.get('balance') + '/text()').extract()[0]
    # item['name'] = response.meta.get('name')
    # item['issue'] = sel.xpath(response.meta.get('issue') + '/text()').extract()[0]
    # item['key'] = response.meta.get('key')
    # item['open_time'] = sel.xpath(response.meta.get('open_time') + '/text()').extract()[-1]
    # if len(sel.xpath(response.meta.get('result'))) == 1:
    #     item['result'] = sel.xpath(response.meta.get('result')).extract()
    # else:
    #     item['result'] = sel.xpath(response.meta.get('result') + '/text()').extract()
    # item['sales'] = sel.xpath(response.meta.get('sales') + '/text()').extract()[0]
    # item['src'] = response.meta.get('src')
    # from helper import get_detail_list
    # detail_list = get_detail_list(sel,response)
    # print detail_list

if __name__ == '__main__':
    func()
# import re
# re.search("\"phase\":\"(.*?)\"", str)