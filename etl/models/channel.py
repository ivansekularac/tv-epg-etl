from mongoengine import Document
from mongoengine import IntField, StringField


class Channel(Document):

    channel_id = IntField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()
    logo = StringField()
