#from scrapy.exceptions import DontCloseSpider
from scrapy.spider import Spider
from scrapy import signals, Request
from scrapy.contrib.loader import ItemLoader
from scrapy.item import Item, Field
import json, collections
from bs4 import BeautifulSoup
from urlparse import urljoin
from HTMLParser import HTMLParser
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

class FocraSpider(Spider):
	name = 'focras'
	'''
	To access scrapy's core API. basically can modify anything in the 'crawler'
	'''
	@classmethod
	def from_crawler(cls, crawler, **kwargs):
		print "focras - from crawler"
		spider = cls(settings=crawler.settings, **kwargs)
		crawler.signals.connect(spider.dont_close_me ,signals.spider_idle)
		return spider
	
	def __init__(self, settings=None, **kwargs):
		super(FocraSpider, self).__init__(**kwargs)
		print 'focras init() kwargs seeds ' + kwargs.get('seeds')
		print 'focras init() kwargs template '+ self.template
		try:
			self.base_url = kwargs.get('seeds').split(',')
			if self.base_url[0].startswith('http://'):
				print self.base_url[0]
				self.start_urls = self.base_url
			else:
				try:
					self.db = client[settings['MONGODB_DB']]
					collection = self.db[self.base_url.pop()]
					fieldname = self.base_url.pop()
					links = collection.find({}, {fieldname: 1})
					client.close()
					temp = []
					for link in links:
						if link.get(fieldname):
							soup = BeautifulSoup(link.get(fieldname))
							temp.append(soup.a['href'])
					self.base_url = temp
					self.start_urls = temp
				except Exception as err:
					print err
			self.template = json.loads(self.template, object_pairs_hook=collections.OrderedDict)
			self.item = Item()
			self.pager = HTMLParser().unescape(self.pager)
		except Exception as error:
			print error

	def dont_close_me(self):
		try:
			db = client['FocraDB']
			collection = db['crawler']
			collection.update({"_id": self.cname}, {"$set":{'crawlerStatus':'stopped'}})
		except Exception as err:
			print err
		print 'closing'
	
	def parse(self, response):		
		try:
			print "Focras - parsing item"
			body = BeautifulSoup(response.body)
			for tag in body.find_all('a', href=True):
				if 'http' not in tag['href']:
					tag['href'] = urljoin(self.base_url[0], tag['href'])
			for tag in body.find_all('img', src=True):
				if 'http' not in tag['src']:
					tag['src'] = urljoin(self.base_url[0], tag['src'])
			for t in body.find_all('tbody'):
				t.unwrap()
			response = response.replace(body=body.prettify(encoding='ascii'))
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
			if self.pager != 'null':
				nextlink = response.xpath('//a[text()[normalize-space()="'+ self.pager +'"]]/@href').extract()
				if nextlink:
					if not nextlink[0].startswith('http://'):
						nextlink[0] = urljoin(self.base_url[0], nextlink.pop())
					print 'next link is ' + nextlink[0]
					yield Request(nextlink[0], callback=self.parse)
		except Exception as err:
			print err