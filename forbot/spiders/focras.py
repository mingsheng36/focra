
from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider
from scrapy import signals 


class FocraSpider(Spider):

	name = 'focras'
	
	def __init__(self, *args, **kwargs):
		super(FocraSpider, self).__init__(*args, **kwargs)
		#self.template = kwargs.get('template')
		print 'From spider init() '+ self.template
		#print self.seeds
		#print self.start_urls
		print kwargs.get('seeds')
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
		try:
			#print response.body
			from scrapy.item import Item
			item = Item()
			row = dict(
			foo='bar',
			baz=[123, 'test'],
			)
			row['url'] = response.url
			if 'finger' in response.url:
				row['digit'] = 'my finger'
				row['appendage'] = 'hand'
			else:
				row['foot'] = 'might be my toe'

			item['row'] = row
			#return item
		
# 			import json
# 			import collections
# 			self.template = json.loads(self.template, object_pairs_hook=collections.OrderedDict)
# 			print self.template
# 			from scrapy.contrib.loader import ItemLoader
# 			from scrapy.item import Field
# 			from scrapy.item import Item
# 			item = Item()
# 			l = ItemLoader(item=item, response=response)
# 			for key, value in self.template.iteritems():
# 				item.fields[key] = Field()
# 				l.add_xpath(key, value)
# 				print key
# 				print value
# 			l.load_item()
# 			print item.keys()
# 			print item.items()
# 			return item
		except Exception as err:
			print err

		print 'crawled response'
		#print response.body
	
	