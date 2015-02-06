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
no_of_links_to_load = 50

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
		crawler.signals.connect(spider.idle, signals.spider_idle)
		return spider
	
	def __init__(self, settings=None, **kwargs):
		super(FocraSpider, self).__init__(**kwargs)
		print 'focras init(' + self.cname + ') kwargs seeds ' + kwargs.get('seeds')
		print 'focras init(' + self.cname + ') kwargs template '+ self.template
		self.queue = Queue.Queue()
		self.queue_counter = 0
		self.queue_reload_counter = 0
		self.next_page_link = 'null'
		self.end_of_data = False
		
		try:
			# non baby crawler
			self.base_url = kwargs.get('seeds').split(',')
			if self.base_url[0].startswith('http'):
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
					cursor = collection.find({}, {self.fieldname: 1}).limit(no_of_links_to_load)
					# set the queue reload counter
					self.queue_reload_counter += no_of_links_to_load
					client.close()
					if cursor.count() <= self.queue_reload_counter:
						print self.cname + '- No more links to load'
						self.end_of_data = True
					# put it into queue
					for link in cursor:
						if link.get(self.fieldname):
							soup = BeautifulSoup(link.get(self.fieldname))
							print soup.a['href']
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
	
	# interrupted state, crawler status determined by views.py
	def stopped(self):
		try:
			print self.cname + " - Stopped"
			db = client['FocraDB']
			collection = db['crawler']
			# baby crawler
			if self.queue_counter != 0:
				collection.update({"_id": self.cname}, {"$set":{'queue_counter': self.queue_counter}})
				print self.cname + " - Queue counter is: " + str(self.queue_counter)
			# pager
			if self.pager != 'null':
				collection.update({"_id": self.cname}, {"$set":{'next_page_link': self.next_page_link}})
				print self.cname + " - Saved pager link is: " + str(self.next_page_link)
			client.close()
		except Exception as err:
			print err
	
	# closed gracefully, crawler status complete
	def idle(self):
		db = client['FocraDB']
		collection = db['crawler']
		collection.update({"_id": self.cname}, {"$set":{'crawlerAddr': '', 'crawlerStatus': 'completed'}})
		print self.cname + " - Crawl completed, closing gracefully"
		client.close()
			
	def parse(self, response):		
		try:
			print self.cname + " - Parsing items"
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
					if not nextlink[0].startswith('http'):
						nextlink[0] = urljoin(self.base_url[0], nextlink.pop())
					print self.cname + ' - Next page is: ' + nextlink[0]
					# to save the state of the pagination
					self.next_page_link = nextlink[0]
					yield Request(nextlink[0], callback=self.parse, dont_filter=True)
				else:
					if not self.queue.empty():
						yield Request(self.queue.get(), callback=self.parse, dont_filter=True)
						self.queue_counter += 1
						if self.queue.qsize() <= no_of_links_to_load and self.end_of_data == False:
							self.check_queue()
			else:
				if not self.queue.empty():
					yield Request(self.queue.get(), callback=self.parse, dont_filter=True)
					self.queue_counter += 1
					if self.queue.qsize() <= no_of_links_to_load and self.end_of_data == False:
						self.check_queue()
		except Exception as err:
			print err

	def check_queue(self):
		try:
			print self.cname + '- Reload counter ' + str(self.queue_reload_counter)
			print self.cname + '- Queue less than ' + str(no_of_links_to_load) + ', querying for more links'
			db = client[self.mongodb_name]
			collection = db[self.parentname]
			cursor = collection.find({}, {self.fieldname: 1}).skip(self.queue_reload_counter).limit(no_of_links_to_load)
			client.close()
			self.queue_reload_counter += no_of_links_to_load
			# cursor count returns the total row
			if cursor.count() <= self.queue_reload_counter:
				print self.cname + '- No more links to load'
				self.end_of_data = True
			# put it into queue
			for link in cursor:
				if link.get(self.fieldname):
					soup = BeautifulSoup(link.get(self.fieldname))
					print soup.a['href']
					self.queue.put(soup.a['href'])
		except Exception as err:
			print err			