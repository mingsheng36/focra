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
import Queue

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
		crawler.signals.connect(spider.stopped, signals.engine_stopped)
		return spider
	
	def __init__(self, settings=None, **kwargs):
		super(FocraSpider, self).__init__(**kwargs)
		print 'focras init(' + self.cname + ') kwargs seeds ' + kwargs.get('seeds')
		print 'focras init(' + self.cname + ') kwargs template '+ self.template
		self.queue = Queue.Queue()
		self.queue_counter = 0
		self.next_page_link = 'null'
		
		try:
			# non baby crawler
			self.base_url = kwargs.get('seeds').split(',')
			if self.base_url[0].startswith('http://'):
				# start the crawling
				self.start_urls = self.base_url
			else:
				# baby crawler
				try:
					# get parent and field info from seeds
					self.parentname = self.base_url.pop()
					self.fieldname = self.base_url.pop()
					# connect using parent name and get first 100 of the field name
					self.mongodb_name = settings['MONGODB_DB']
					db = client[self.mongodb_name]
					collection = db[self.parentname]
					links = collection.find({}, {self.fieldname: 1}).limit(100)
					client.close()
					# put it into queue
					for link in links:
						if link.get(self.fieldname):
							soup = BeautifulSoup(link.get(self.fieldname))
							self.queue.put(soup.a['href'])
					# dequeue and start the crawling
					self.base_url = [self.queue.get()]
					self.queue_counter += 1
					self.start_urls = self.base_url
				except Exception as err:
					print err
			self.template = json.loads(self.template, object_pairs_hook=collections.OrderedDict)
			self.item = Item()
			self.pager = HTMLParser().unescape(self.pager)
		except Exception as error:
			print error
	
	def stopped(self):
		# update crawler status when the job has finished
		try:
			db = client['FocraDB']
			collection = db['crawler']
			# baby crawler
			if self.queue_counter != 0:
				collection.update({"_id": self.cname}, {"$set":{'crawlerStatus':'stopped', 'queue_counter': self.queue_counter, 'crawlerAddr': ''}})
				print "STOPPING " + self.cname + " - queue counter is: " + str(self.queue_counter)
			# pager
			if self.pager != 'null':
				collection.update({"_id": self.cname}, {"$set":{'crawlerStatus':'stopped', 'next_page_link': self.next_page_link, 'crawlerAddr': ''}})
				print "STOPPING " + self.cname + " next page link is: " + str(self.next_page_link)
			# normal scraping
			if self.queue_counter == 0 and self.pager == 'null':
				collection.update({"_id": self.cname}, {"$set":{'crawlerStatus':'stopped', 'crawlerAddr': ''}})
				print "STOPPING " + self.cname
			client.close()
		except Exception as err:
			print err
	
	def parse(self, response):		
		try:
			print self.cname + " - parsing item"
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
					print 'Next page for ' + self.cname + ': ' + nextlink[0]
					# to save the state of the pagination
					self.next_page_link = nextlink[0]
					yield Request(nextlink[0], callback=self.parse)
				else:
					if not self.queue.empty():
						print 'Next link from queue for ' + self.cname + ':'
						yield Request(self.queue.get(), callback=self.parse)
						self.queue_counter += 1
						self.check_queue()
			else:
				if not self.queue.empty():
					print 'Next link from queue for ' + self.cname + ':'
					yield Request(self.queue.get(), callback=self.parse)
					self.queue_counter += 1
					self.check_queue()
				
		except Exception as err:
			print err

	def check_queue(self):
		if self.queue.qsize() <= 20:
			print 'queue less than 3, adding..'
	
# 	def get_links(self):
# 		self.db = client[self.mongodb_name]
# 		collection = self.db[self.parentname]
# 		links = collection.find({}, {self.fieldname: 1}).limit(100)
# 		client.close()