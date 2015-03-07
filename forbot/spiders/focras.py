from scrapy.spider import Spider
from scrapy import signals, Request
from scrapy.contrib.loader import ItemLoader
from scrapy.item import Item, Field
from scrapy.exceptions import CloseSpider
import json, collections
from bs4 import BeautifulSoup
from urlparse import urljoin
from HTMLParser import HTMLParser
from pymongo import MongoClient
import Queue
import time

client = MongoClient('localhost', 27017)
LINK_NUMBER = 50

class FocraSpider(Spider):
	name = 'focras'
	'''
	To access scrapy's core API. basically can modify anything in the 'crawler'
	'''
	@classmethod
	def from_crawler(cls, crawler, **kwargs):
		print "focras - from crawler"
		spider = cls(stats=crawler.stats, settings=crawler.settings, **kwargs)
		crawler.signals.connect(spider.stopped, signals.engine_stopped)
		crawler.signals.connect(spider.idle, signals.spider_idle)
		return spider
	
	def __init__(self, stats=None, settings=None, **kwargs):
		super(FocraSpider, self).__init__(**kwargs)
		try:
			self.start_time = time.time()
			print 'focras init(' + self.cname + ') kwargs seeds ' + kwargs.get('seeds')
			print 'focras init(' + self.cname + ') kwargs template '+ self.template
			self.queue = Queue.Queue()
			self.queue_counter = 0
			self.queue_reload_counter = 0
			# to save the state of the pagination
			self.next_page_link = None
			self.end_of_data = False
			self.template = json.loads(self.template, object_pairs_hook=collections.OrderedDict)
			self.item = Item()
			self.pager = HTMLParser().unescape(self.pager)
			self.base_url = kwargs.get('seeds').split(',')
			self.crawled_pages = 0
			self.status = None
			
			# non chain crawler dont have a queue, check for pager only
			# chain crawler url does not start with http
			if self.base_url[0].startswith('http'):
				# for request_url of chain crawler
				self.parentname = None
				if self.runtype == 'resume' and self.pager != 'null':
					db = client['FocraDB']
					collection = db['crawler']
					cursor_focra = collection.find_one({'_id':self.cname})
					self.base_url = [cursor_focra.get('next_page_link')]
					self.crawled_pages = cursor_focra.get('crawled_pages')
					self.start_time = self.start_time - cursor_focra.get('time_executed')
					client.close()
					print self.cname + " - Resume page is: " + self.base_url[0]
					self.start_urls = self.base_url
				else:
					print self.cname + " - Start page is: " + self.base_url[0]
					self.start_urls = self.base_url
			else:
				# chain crawler
				# get parent and field info from seeds
				self.parentname = self.base_url.pop()
				self.fieldname = self.base_url.pop()
				# connect using parent name and get first 100 of the field name
				self.crawler_db = settings['CRAWLER_DB']
				db = client[self.crawler_db]
				collection = db[self.parentname]
				if self.runtype == 'resume':
					db_focra = client['FocraDB']
					cursor_focra = db_focra['crawler'].find_one({'_id': self.cname})
					self.queue_counter = cursor_focra.get('queue_counter')
					self.next_page_link = cursor_focra.get('next_page_link')
					self.crawled_pages = cursor_focra.get('crawled_pages')
					self.start_time = self.start_time - cursor_focra.get('time_executed')
					print self.cname + " - Loading Queue from " + str(self.queue_counter)
					cursor = collection.find({}, {self.fieldname: 1}).skip(self.queue_counter).limit(LINK_NUMBER)
					self.queue_reload_counter = self.queue_reload_counter + LINK_NUMBER + self.queue_counter
				else:
					cursor = collection.find({}, {self.fieldname: 1}).limit(LINK_NUMBER)
					# set the queue reload counter
					self.queue_reload_counter += LINK_NUMBER
				client.close()
				
				if cursor.count() <= self.queue_reload_counter:
					print self.cname + '- No more links to load'
					self.end_of_data = True
						
				# put it into queue
				for link in cursor:
					if link.get(self.fieldname):
						soup = BeautifulSoup(link.get(self.fieldname))
						# to see the links added to queue
						print soup.a['href']
						self.queue.put(soup.a['href'])
				
				# if resume
				if self.next_page_link:
					self.base_url = [self.next_page_link]
					print self.cname + " - Resume page is: " + self.base_url[0]
					self.start_urls = self.base_url
				else:
					self.base_url = [self.queue.get()]
					if self.queue_counter == 0:
						self.queue_counter += 1
						print self.cname + " - Start page is: " + self.base_url[0]
					else:
						print self.cname + " - Resume page is: " + self.base_url[0]
					self.start_urls = self.base_url
		except Exception as error:
			print error
	
	# interrupted state, crawler status determined by views.py
	# it is stopped or paused
	def stopped(self):
		try:
			if self.runtype != 'complete':
				print self.cname + " - Stopped"
				db = client['FocraDB']
				collection = db['crawler']
				# chain crawler queue from parent crawler
				if self.queue_counter != 0:
					collection.update({"_id": self.cname}, {"$set":{'queue_counter': self.queue_counter, 
																 	'crawled_pages': self.crawled_pages,
																 	'time_executed': time.time() - self.start_time}})
					print self.cname + " - Saved queue counter is: " + str(self.queue_counter)
				# main or chained crawler pager state
				if self.pager != 'null' and self.next_page_link:
					collection.update({"_id": self.cname}, {"$set":{'next_page_link': self.next_page_link,
																 	'crawled_pages': self.crawled_pages,
																 	'time_executed': time.time() - self.start_time}})
					print self.cname + " - Saved Page link is: " + str(self.next_page_link)
				client.close()
		except Exception as err:
			print err
	
	# closed gracefully, crawler status complete
	def idle(self):
		try:
			# crawl completed
			if self.status == 'running':
				db = client['FocraDB']
				collection = db['crawler']
				collection.update({"_id": self.cname}, {"$set":{'crawlerAddr': '',
																'crawlerStatus': 'completed',
																'crawled_pages': self.crawled_pages,
																'time_executed': time.time() - self.start_time}})
				print self.cname + " - Crawl completed, closing gracefully"
				self.runtype = 'complete'
				client.close()
		except Exception as err:
			print err
			
	def parse(self, response):		
		try:
			self.crawled_pages += 1
			db = client['FocraDB']
			db['crawler'].update({"_id": self.cname}, {"$set":{'crawled_pages': self.crawled_pages,
																'time_executed': time.time()-self.start_time}})
			
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
			
			if self.parentname is not None:
				self.item.fields['request_url'] = Field()
				dynamicItemLoader.add_value("request_url", response.url)
				
			for key, value in self.template.iteritems():
				self.item.fields[key] = Field()
				dynamicItemLoader.add_xpath(key, value)
			
			yield dynamicItemLoader.load_item()
			
			# after scraping the page, check status to see whether we should stop
			self.status = db['crawler'].find_one({"_id":self.cname}).get('crawlerStatus')
			if self.status == 'stopped' or self.status == 'paused':
				raise CloseSpider('stopped')
			
			# check for pagination
			if self.pager != 'null':
				next_link = None
				# if the pager is in html format
				if bool(BeautifulSoup(self.pager, "html.parser").find()):
					# remove the \r for 'end of line' diff
					self.pager = self.pager.replace('\r', '')
					a_tags = response.xpath('//a').extract()
					for tag in a_tags:
						if self.pager in tag:
							tag = BeautifulSoup(tag)
							next_link = tag.a.get('href')
							break
				# if the pager is in text format
				else:
					if response.xpath('//a[text()[normalize-space()="'+ self.pager +'"]]/@href').extract():
						next_link = response.xpath('//a[text()[normalize-space()="'+ self.pager +'"]]/@href').extract()[0]
				
				if next_link:
					self.next_page_link = next_link
					print self.cname + ' - Next page is: ' + self.next_page_link
					yield Request(self.next_page_link, callback=self.parse, dont_filter=True)
					
				else:
					# chained crawler WITH pagination
					# check for more links from parent column
					if not self.queue.empty():
						yield Request(self.queue.get(), callback=self.parse, dont_filter=True)
						self.queue_counter += 1
						if self.queue.qsize() <= LINK_NUMBER and self.end_of_data == False:
							self.check_queue()
			else:
				# chained crawler WITHOUT pagination
				# check for more links from parent column
				if not self.queue.empty():
					yield Request(self.queue.get(), callback=self.parse, dont_filter=True)
					self.queue_counter += 1
					if self.queue.qsize() <= LINK_NUMBER and self.end_of_data == False:
						self.check_queue()
	
		except Exception as err:
			print err

	def check_queue(self):
		try:
			print self.cname + '- Reload counter ' + str(self.queue_reload_counter)
			print self.cname + '- Queue less than ' + str(LINK_NUMBER) + ', querying for more links'
			db = client[self.crawler_db]
			collection = db[self.parentname]
			cursor = collection.find({}, {self.fieldname: 1}).skip(self.queue_reload_counter).limit(LINK_NUMBER)
			client.close()
			self.queue_reload_counter += LINK_NUMBER
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