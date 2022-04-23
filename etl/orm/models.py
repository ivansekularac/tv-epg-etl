from mongoengine import (
    DateTimeField,
    Document,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)


class Channel(Document):

    channel_id = IntField(required=True, unique=True)
    original_id = IntField()
    name = StringField(required=True)
    logo = StringField()
    category = ListField(field=StringField())

    def __str__(self):
        return self.name


class Show(Document):

    title = StringField(required=True)
    category = StringField()
    description = StringField()
    start_dt = DateTimeField()
    end_dt = DateTimeField()
    start_ts = IntField()
    end_ts = IntField()
    duration = FloatField()
    poster = StringField()
    channel_id = ReferenceField(Channel)

    def __str__(self):
        return self.title
