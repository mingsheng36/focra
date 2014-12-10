
from mongoengine import Document, StringField
 
class User(Document):
    username = StringField(primary_key=True, unique=True, required=True)
    password = StringField(max_length=50, required=True)


