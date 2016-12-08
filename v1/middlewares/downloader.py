# -*- coding: utf-8 -*-
import sys
sys.path.append(r'D:\virtualenv\caipiao\venv')
import time
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse, Response
from pip import basecommand
from selenium import webdriver
import selenium.webdriver.support.ui as ui


class CustomDownloader(object):
    def __init__(self):
        # use any browser you wish
        # cap = webdriver.DesiredCapabilities.PHANTOMJS
        # cap["phantomjs.page.settings.resourceTimeout"] = 1000
        # cap["phantomjs.page.settings.loadImages"] = False
        # cap["phantomjs.page.settings.disk-cache"] = True
        # cap["phantomjs.page.customHeaders.Cookie"] = 'SINAGLOBAL=3955422793326.2764.1451802953297; '
        #self.driver = webdriver.PhantomJS(executable_path='D:/Program Files/phantomjs/bin/phantomjs.exe', desired_capabilities=cap)
        # wait = ui.WebDriverWait(self.driver, 10)
        chromedriver = r"C:\Users\yao\AppData\Local\Google\Chrome\Application\chromedriver.exe"
        self.driver = webdriver.Chrome(chromedriver)

    def VisitPersonPage(self, url):
        print(u'正在加载网站.....')
        self.driver.get(url)
        time.sleep(2)
        # 翻到底，详情加载
        # js = "var q=document.documentElement.scrollTop=10000"
        # self.driver.execute_script(js)
        # time.sleep(2)
        content = self.driver.page_source.encode('utf-8', 'ignore')
        print(u'网页加载完毕.....')
        return content

    def __del__(self):
        self.driver.close()