
from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider
from scrapy import signals 
from scrapy.contrib.loader import ItemLoader
from scrapy.item import Item, Field
import json, collections

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
			self.item = Item()
		except Exception as error:
			print error
		
	
	def dont_close_me(self):
		raise DontCloseSpider("Not Closed")
	
	def parse(self, response):		
		try:
			print "Focras - parsing item"
			dynamicItemLoader = ItemLoader(item=self.item, response=response)
			for key, value in self.template.iteritems():
				print key
				#print key, value
				self.item.fields[key] = Field()
				dynamicItemLoader.add_xpath(key, value)
			yield dynamicItemLoader.load_item()
			
		except Exception as err:
			print err