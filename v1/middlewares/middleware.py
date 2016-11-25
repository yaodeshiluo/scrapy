# -*- coding: utf-8 -*-

from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse, Response

import v1.middlewares.downloader as downloader


class CustomMiddlewares(object):
    def process_request(self, request, spider):
        if request.meta.get('webdriver'):
            url = str(request.url)
            dl = downloader.CustomDownloader()
            content = dl.VisitPersonPage(url)
            if request.meta.get('webdriver') == 'once':
                request.meta['webdriver'] = None
            return HtmlResponse(url, status=200, body=content, request=request)
        return None

    def process_response(self, request, response, spider):
        if len(response.body) == 100:
            return IgnoreRequest("body length == 100")
        else:
            return response