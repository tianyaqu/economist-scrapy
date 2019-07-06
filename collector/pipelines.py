# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import redis
import datetime
from collector.summary import Summary
from collector.model import Edition, Article
from collector.singleton import Singleton
from peewee import fn

class CollectorPipeline(object):
    __metaclass__ = Singleton
   
    def __init__(self,host, port, passwd):
        self.summary = Summary()
        self.redis_host = host
        self.redis_port = port
        self.redis_passwd = passwd

    @classmethod 
    def from_crawler(cls, crawler):
        redis_conf = crawler.settings.getdict("REDIS_CONFIG")
        return cls(
            host = redis_conf.get('host'),
            port = redis_conf.get('port'),
            passwd = redis_conf.get('passwd')
        )

    
    def add_article(self,date,section,title,fly,desc,id,origin,content,images, summary):
        try:
            a = Article(edition=date,section=section,title=title,fly=fly,rubric=desc,name=id,origin=origin,content=content,imgs=images,summary=summary,tsv=fn.to_tsvector(content))
            a.save()
        except Exception as e:
            print('insert article error ',e)

    def add_edition(self,date,cover):
        try :
            ed = Edition(edition=date, cover=cover)
            ed.save()
        except Exception as e:  
            print('insert edition error ',e)
            pass   

    def genList(self, name, edition, section, order) :
        smap = {
            "The world this week": 1,
            "Leaders" : 2,
            "Letters" : 3,
            "Briefing": 4,
            "United States":5,
            "The Americas" : 6,
            "Asia":7,
            "China" : 8,
            "Middle East and Africa" : 9,
            "Europe" : 10,
            "Britain" : 11,
            "International" : 12,
            "Special Report" : 13,
            "Business" : 14,
            "Finance and economics" : 15,
            "Science and technology": 16,
            "Books and arts" : 17,
            "Obituary" : 18,
            "Economic and financial indicators" : 19,
        }

        score = order
        sec = '0'
        if section in smap :
            score += smap[section] * 20 
            sec = str(smap[section])
        volKey = 'eco_edition_' + edition.strftime('%Y%m%d')
        secKey = 'eco_edition_' + edition.strftime('%Y%m%d') + "_" + sec
        r = redis.Redis(host=self.redis_host, port=self.redis_port,password=self.redis_passwd ,decode_responses=True)
        item = {
            name : score,
        }
        r.zadd(volKey, item)
        r.zadd(secKey, item)
        print(name,' sec: ', section, ' order ',order, ' score ', score)

    def process_item(self, item, spider):
        if item.get('atype', 0) == 1 :
            spider.logger.info('type editon cover %s %s',  item['cover'], item['edition'].strftime('%Y%m%d'))
            self.add_edition(item['edition'], item.get('cover',''))
            print('insert edition ', item.get('edition',''))
        else :
            summ = ""
            content = item.get('content','')
            if len(content) > 0:
                summ = self.summary.gen(item.get('title',''), content)
            self.add_article(item['edition'], item.get('section',''), item.get('title',''), item.get('fly',''), item.get('desc',''), item.get('name',''), item['url'], content, item.get('imgs',[]), summ)
            print('insert article ', item.get('url',''), ' summary ', summ)
            self.genList(item.get('name',''), item['edition'], item.get('section',''), item.get('order',0))
        return item
