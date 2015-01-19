# -*- coding: utf-8 -*-

# Scrapy settings for fobot project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'forbot'
USER_AGENT = 'Mozilla/5.0'

SPIDER_MODULES = ['forbot.spiders']
NEWSPIDER_MODULE = 'forbot.spiders'

EXTENSIONS = {
     'scrapy.telnet.TelnetConsole': None,
}

ITEM_PIPELINES = {'forbot.pipelines.MongoDBPipeline':10}

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "CrawlerDB"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'fobot (+http://www.yourdomain.com)'
