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
        client = MongoClient(self.settings['MONGODB_SERVER'], self.settings['MONGODB_PORT'])
        self.crawler_db = client[self.settings['CRAWLER_DB']]
        
    '''
    data extracted per xpath are in a list format, separated by '\r\n' or maybe '\n'
    need to join them together
    '''
    def process_item(self, item, spider):
        try:
            crawler_collection = self.crawler_db[spider.cname]
            # remove null values
            most_length = 0
            for i in item:
                z = item.get(i)
                for j in range(len(z)):
                    z[j] = z[j].strip()
                    z[j] = z[j].rstrip('\n')
                item[i] = filter(None, z)
                if len(item.get(i)) > most_length:
                    most_length = len(item.get(i))
            
            # put them in a row
            for j in range(most_length):
                row = {}
                for k in item.keys():
                    row[k] = None
                    try:
                        if item.get(k)[j].strip():
                            row[k] = item.get(k)[j]
                    except Exception:
                        pass
                crawler_collection.insert(row)
            print 'pipline - Inserted ' + str(most_length) + ' rows'
        except Exception as err:
            print err