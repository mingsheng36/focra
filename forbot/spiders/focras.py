
from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider
from scrapy import signals, Request
from scrapy.contrib.loader import ItemLoader
from scrapy.item import Item, Field
import json, collections
from bs4 import BeautifulSoup
from urlparse import urljoin
from HTMLParser import HTMLParser

class FocraSpider(Spider):
	name = 'focras'
	'''
	To access scrapy's core API. basically can modify anything in the 'crawler'
	'''
	@classmethod
	def from_crawler(cls, crawler, **kwargs):
		print "focras - from crawler"
		spider = cls(**kwargs)
		crawler.signals.connect(spider.dont_close_me ,signals.spider_idle)
		return spider
	
	def __init__(self, **kwargs):
		super(FocraSpider, self).__init__(**kwargs)
		print 'focras init() kwargs seeds ' + kwargs.get('seeds')
		print 'focras init() kwargs template '+ self.template
		try:
			self.template = json.loads(self.template, object_pairs_hook=collections.OrderedDict)
			self.start_urls =  kwargs.get('seeds').split(',')
			self.base_url = self.start_urls
			self.item = Item()
			self.pager = HTMLParser().unescape(self.pager)
		except Exception as error:
			print error

	def dont_close_me(self):
		raise DontCloseSpider("Not Closed")
	
	def parse(self, response):		
		try:
			print "Focras - parsing item"
			body = BeautifulSoup(response.body)
			for t in body.find_all('tbody'):
				t.unwrap()
			response = response.replace(body=str(body.prettify()))
			dynamicItemLoader = ItemLoader(item=self.item, response=response)
			for key, value in self.template.iteritems():
				self.item.fields[key] = Field()
				dynamicItemLoader.add_xpath(key, value)
				'''
				data extracted per xpath are in a list format, separated by '\r\n' or maybe '\n'
				need to join them together
				'''
			yield dynamicItemLoader.load_item()
			
			# check for pagination
			nextlink = response.xpath('//a[text()[normalize-space()="'+ self.pager +'"]]/@href').extract()
			if nextlink:
				print 'next link is ' + nextlink[0]
				pager_sanitized = urljoin(self.base_url[0], nextlink.pop())
				print 'pager sanitized is ' + pager_sanitized
				yield Request(pager_sanitized, callback=self.parse)
		except Exception as err:
			print err