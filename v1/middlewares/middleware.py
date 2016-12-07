# -*- coding: utf-8 -*-

from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse, Response, Request
from scrapy import signals
import v1.middlewares.downloader as downloader
import random


class CustomMiddlewares(object):
    def process_request(self, request, spider):
        if request.meta.get('webdriver'):
            url = str(request.url)
            dl = downloader.CustomDownloader()
            content = dl.VisitPersonPage(url)
            if request.meta.get('webdriver') == 'once':
                request.meta['webdriver'] = None
            return HtmlResponse(url, status=200, body=content, request=request)
        # if not request.meta.get('urllist'):
        #     return Request(request.meta.get('website'), dont_filter=True, meta=request.meta,callback=Spider1.parse_all_in_one)
        return None

    def process_response(self, request, response, spider):
        if len(response.body) == 100:
            return IgnoreRequest("body length == 100")
        else:
            return response

class MyUserAgentMiddleware(object):
    """This middleware allows spiders to override the user_agent"""

    def __init__(self, user_agent='Scrapy'):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings['USER_AGENT'])
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, 'user_agent', self.user_agent)

    def process_request(self, request, spider):
        if self.user_agent:
            if isinstance(self.user_agent,list):
                ua = random.choice(self.user_agent)
                request.headers.setdefault(b'User-Agent', ua)
            else:
                request.headers.setdefault(b'User-Agent', self.user_agent)