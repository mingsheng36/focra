# -*- coding: utf-8 -*-
'''
Created on 9 Mar 2015

@author: Tan Ming Sheng
'''
BOT_NAME = 'forbot'
USER_AGENT = 'Mozilla/5.0'

SPIDER_MODULES = ['forbot.spiders']
NEWSPIDER_MODULE = 'forbot.spiders'

EXTENSIONS = {
     'scrapy.telnet.TelnetConsole': None,
     'scrapy.webservice.WebService': None,
     'scrapy.contrib.memusage.MemoryUsage': None,
     'scrapy.contrib.memdebug.MemoryDebugger': None,
     'scrapy.contrib.logstats.LogStats': None,
}

ITEM_PIPELINES = {'forbot.pipelines.MongoDBPipeline':10}

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
CRAWLER_DB = "CrawlerDB"
FOCRA_DB = "FocraDB"

DOWNLOAD_DELAY = 2
COOKIES_ENABLED = False
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'fobot (+http://www.yourdomain.com)'
