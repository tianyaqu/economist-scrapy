# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Identity


class CollectorItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    edition = scrapy.Field()
    section = scrapy.Field()
    desc    = scrapy.Field()
    fly = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()
    imgs = scrapy.Field(
        output_processor = Identity()
    )
    section = scrapy.Field()
    cover   = scrapy.Field()
    atype  = scrapy.Field()
    
    pass
