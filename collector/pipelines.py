# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import datetime
from collector.summary import Summary
from collector.model import Edition, Article
from collector.singleton import Singleton
from peewee import fn

class CollectorPipeline(object):
    __metaclass__ = Singleton
   
    def __init__(self,db, user, passwd):
        self.summary = Summary()

    @classmethod 
    def from_crawler(cls, crawler):
        psql_conf = crawler.settings.getdict("POSTGRESQL_CONFIG")
        return cls(
            db = psql_conf.get('db'),
            user = psql_conf.get('user'),
            passwd = psql_conf.get('passwd')
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
        return item
