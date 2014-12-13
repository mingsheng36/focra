
from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider
from scrapy import signals 
#from scrapy.crawler import CrawlerProcess

class FocraSpider(Spider):

	name = 'focras'
	
	def __init__(self, *args, **kwargs):
		super(FocraSpider, self).__init__(*args, **kwargs)
		print kwargs.get('seeds')
		self.start_urls = [kwargs.get('seeds')]
	
	####
	# To access scrapy's core API. basically can modify anything in the 'crawler'
	####	
	@classmethod
	def from_crawler(cls, crawler, **kwargs):
		spider = cls(**kwargs)
		crawler.signals.connect(spider.dont_close_me ,signals.spider_idle)
		return spider
	
	def dont_close_me(self):
		raise DontCloseSpider("..I prefer live spiders.")
		
	def parse(self, response):
		print response.body
	
	