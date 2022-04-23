from mongoengine import Document
from mongoengine import IntField, StringField, ListField


class Channel(Document):

    channel_id = IntField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()
    logo = StringField()
    category = ListField(field=StringField())

    def __str__(self):
        return self.name
