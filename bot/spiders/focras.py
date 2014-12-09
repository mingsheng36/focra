
from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider
from scrapy import signals 
#from scrapy.crawler import CrawlerProcess

class FocraSpider(Spider):

	name = 'focras'
	start_urls = ['http://forums.hardwarezone.com.sg']
	
	@classmethod
	def from_crawler(cls, crawler):
		cc = cls()
		crawler.signals.connect(cc.dont_close_me ,signals.spider_idle)
		return cc
		
	def dont_close_me(self):
		#print "NO CLOSE ME"
		raise DontCloseSpider("..I prefer live spiders.")
		
	def parse(self, response):
		print "success! lol!!!!"
		#print response.body
	
	