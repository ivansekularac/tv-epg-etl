from mongoengine import Document
from mongoengine import (
    StringField,
    DateTimeField,
    FloatField,
    ReferenceField,
)
from models.channel import Channel


class Show(Document):

    title = StringField(required=True)
    category = StringField()
    description = StringField()
    start = DateTimeField()
    end = DateTimeField()
    duration = FloatField()
    poster = StringField()
    channel_id = ReferenceField(Channel)

