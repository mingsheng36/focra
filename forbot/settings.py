# -*- coding: utf-8 -*-

# Scrapy settings for fobot project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'forbot'

SPIDER_MODULES = ['forbot.spiders']
NEWSPIDER_MODULE = 'forbot.spiders'

EXTENSIONS = {
     'scrapy.telnet.TelnetConsole': None,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'fobot (+http://www.yourdomain.com)'
