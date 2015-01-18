from pymongo import MongoClient

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
        self.crawler = crawler
        client = MongoClient(self.settings['MONGODB_SERVER'], self.settings['MONGODB_PORT'])
        self.db = client[self.settings['MONGODB_DB']]

    def process_item(self, item, spider):
        try:
            collection = self.db[spider.name]
            print "pipline - processing item"
            print item.keys()
            for value in item:
                print value
            collection.insert(dict(item))
        except Exception as err:
            print err