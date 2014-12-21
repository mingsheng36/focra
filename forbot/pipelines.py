import pymongo
from scrapy.exceptions import DropItem

class MongoDBPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):    
        return cls(crawler)    
            
    def __init__(self, crawler):
        self.settings = crawler.settings
        self.crawler = crawler
        print "From pipeline init, hi!"
        connection = pymongo.Connection(self.settings['MONGODB_SERVER'], self.settings['MONGODB_PORT'])
        db = connection[self.settings['MONGODB_DB']]
        self.collection = db['test1']
        
    def process_item(self, item, spider):
        print "Processing item"
        valid = True
        self.collection.insert(dict(item))
        for data in item:
            print data
            #here we only check if the data is not null
            #but we could do any crazy validation we want
            if not data:
                print "data not valid"
                valid = False
                raise DropItem("Missing %s of blogpost from %s" % (data, item['url']))
            if valid:
                print "Item wrote to MongoDB database %s/%s" % (self.settings['MONGODB_DB'], self.settings['MONGODB_COLLECTION']) 
