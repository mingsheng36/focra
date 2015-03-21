'''
Created on 9 Mar 2015

@author: Tan Ming Sheng
'''
from pymongo import MongoClient
from bs4 import BeautifulSoup
from collections import OrderedDict

class MongoDBPipeline(object):
    '''
    To access scrapy's core API. basically can modify anything in the 'crawler'
    '''
    @classmethod
    def from_crawler(cls, crawler):
        print 'pipline - from crawler()'    
        return cls(crawler)
            
    def __init__(self, crawler):
        print "pipline - init()"
        self.settings = crawler.settings
        client = MongoClient(self.settings['MONGODB_SERVER'], self.settings['MONGODB_PORT'])
        self.crawler_db = client[self.settings['CRAWLER_DB']]
        
    '''
    data extracted per xpath are in a list format, separated by '\r\n' or maybe '\n'
    need to join them together
    '''
    def process_item(self, item, spider):
            
        print "ran------------"
        try:
            crawler_collection = self.crawler_db[spider.cname]
            '''
            remove null values
            '''
            #print item
            most_length = 0
            for i in item:
                if len(item.get(i)) > most_length:
                    most_length = len(item.get(i))
            
            bulk = []
            for j in range(most_length):
                row = OrderedDict()
                for i in item:
                    if i == 'request_url':
                        row[i] = item.get(i)[0]
                    else:
                        try:
                            data = item.get(i)[j]
                            if data.startswith('<a'):
                                soup = BeautifulSoup(data).a
                                del soup['class']
                                del soup['style']
                                row[i] = unicode(soup)
                            elif data.startswith('<img'):
                                row[i] = data
                            else:
                                sb = ""
                                for string in BeautifulSoup(data).stripped_strings:
                                    sb += " " + string
                                if sb != "":
                                    row[i] = sb
                        except Exception as err:
                            pass
                temp = row.copy()
                temp.pop("request_url", None)
                if temp:
                    #crawler_collection.insert(row)
                    bulk.append(row)

            if len(bulk) > 0:
                crawler_collection.insert(bulk, {'ordered': 'true'})

            print 'pipline - Inserted ' + str(len(bulk)) + ' rows'
        except Exception as err:
            print err