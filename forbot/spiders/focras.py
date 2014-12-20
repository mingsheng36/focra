
from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider
from scrapy import signals 
from scrapy import log

class FocraSpider(Spider):

	name = 'focras'
	
	def __init__(self, *args, **kwargs):
		super(FocraSpider, self).__init__(*args, **kwargs)
		self.template = kwargs.get('template')
		self.start_urls = [kwargs.get('seeds')]
	
	'''
	To access scrapy's core API. basically can modify anything in the 'crawler'
	'''
	@classmethod
	def from_crawler(cls, crawler, **kwargs):
		spider = cls(**kwargs)
		crawler.signals.connect(spider.dont_close_me ,signals.spider_idle)
		return spider
	
	def dont_close_me(self):
		raise DontCloseSpider("Not Closed")
	
	'''
	parse the response using itemloader
	'''
	def parse(self, response):
		
		from scrapy.contrib.loader import ItemLoader
		from scrapy.item import Field
		from scrapy.item import Item
		item = Item()
		l = ItemLoader(item=item, response=response)
		if self.templates is not None:
			for key, value in self.kwargs.iteritems():
				item.fields[key] = Field()
				l.add_xpath(key, value)
				log.msg(key + ' ' + value, level=log.WARNING)
		print 'crawled response'
		#print response.body
	
	