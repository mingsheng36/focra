
from mongoengine import Document, StringField, ListField
 
class User(Document):
    username = StringField(primary_key=True, unique=True, required=True)
    password = StringField(max_length=50, required=True)

class Crawler(Document):
    crawlerName = StringField(primary_key=True, unique=True, required=True)
    crawlerSeeds = ListField(required=True,)
    crawlerStatus = StringField(required=True)
    crawlerAddr = StringField()
    crawlerOwner = StringField(required=True)
    crawlerTemplate = StringField()