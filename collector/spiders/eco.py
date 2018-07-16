# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.loader import ItemLoader
from collector.items import CollectorItem
from scrapy.loader.processors import TakeFirst
import scrapy
from bs4 import BeautifulSoup
import bs4
import datetime
import shortuuid

class DefaultItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


date = datetime.datetime.now()

class EcoSpider(Spider):
    name = 'eco'
    allowed_domains = ['economist.com']
    start_urls = ['https://www.economist.com/ap/printedition/'] 
    custom_settings = { 
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
        'DOWNLOAD_DELAY' : 3,
        'CONCURRENT_REQUESTS' : 4,
        #'CLOSESPIDER_PAGECOUNT' : 5,
    }

    def parse_item(self, response):
        loader = DefaultItemLoader(item=CollectorItem(), response = response)
        loader.add_value('url', response.url )
        loader.add_value('name', shortuuid.uuid() )
        loader.add_css('fly', 'h1 > span.flytitle-and-title__flytitle::text' )
        loader.add_css('title', 'h1 > span.flytitle-and-title__title::text')
        loader.add_css('desc', '.blog-post__rubric::text')

        sec = response.url.split('/')[-5]
        sec = sec.strip('-')
        loader.add_value('section',sec)

        global date
        loader.add_value('edition', date)


        soup = BeautifulSoup(response.body,"lxml")

        imgUrls = []
        for img in soup.article.find_all('img'):
            srcUrl = img['src']
            imgUrls.append(srcUrl)
        loader.add_value('imgs', imgUrls)

        bad = ['input','data-reactroot','article','itemprop','class','xlink:href','role','tabindex', 'width', 'height','fill','target','itemtype','id', 'alt','sizes','srcset','aria-label', 'title', 'href','style', 'itemscope','rel','type']
        inner = soup.select('.blog-post__inner')[0]
        if inner:
            for x in inner.descendants:
                if isinstance(x, bs4.element.NavigableString): continue
                for attr in list(x.attrs.keys()) : 
                    if attr in bad:
                        del inner[attr]

            #content = [p.prettify() for p in inner.select('p')]
            content = [p.text for p in inner.select('p')]
            c = '\n'.join(content)
            loader.add_value('content', c)

        return loader.load_item()


    def start_requests(self):
            return [scrapy.FormRequest(u,callback=self.parse_start_url) for u in self.start_urls]

    def parse_start_url(self, response):
        root = BeautifulSoup(response.body, "lxml")

        cover = ""
        tags = root.select('.print-edition__cover-widget__image')
        if len(tags) > 0:
            cover = tags[0].img['src']
            dateStr = cover.split('/')[-1].split('_')[0]
            global date
            date = datetime.datetime.strptime(dateStr,"%Y%m%d")
            atype = 1
            item = CollectorItem()
            item['atype'] = atype
            item['cover'] = cover
            item['edition'] = date
            yield item

        urls = [h['href'] for h in root.select(".list__link")]
        for url in urls:
            print('new', response.urljoin(url))
            yield scrapy.Request(response.urljoin(url),callback=self.parse_item)
