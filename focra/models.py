'''
Created on 9 Mar 2015

@author: Tan Ming Sheng
'''
from mongoengine import Document, StringField, ListField, DateTimeField
 
class User(Document):
    username = StringField(primary_key=True, unique=True, required=True)
    password = StringField(max_length=50, required=True)

class Crawler(Document):
    crawlerName = StringField(primary_key=True, unique=True, required=True)
    crawlerSeeds = ListField(required=True,)
    crawlerStatus = StringField(required=True)
    crawlerPager = StringField()
    crawlerOwner = StringField(required=True)
    crawlerParent = StringField()
    crawlerChain = StringField()
    crawlerCreated = DateTimeField()
    queue_counter = StringField()
    next_page_link = StringField()
    crawled_pages = StringField()
    rows_inserted = StringField()
    time_executed = StringField()
    '''
    Because mongoengine does not support ordered-dict-field yet. store as string to maintain order
    '''
    crawlerTemplate = StringField()
