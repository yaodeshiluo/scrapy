# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class V1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    balance = scrapy.Field()
    website= scrapy.Field()
    issue = scrapy.Field()
    key= scrapy.Field()
    name = scrapy.Field()
    open_time = scrapy.Field()
    result = scrapy.Field()
    sales = scrapy.Field()
    src = scrapy.Field()
    detail = scrapy.Field()

    url = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    status = scrapy.Field()

