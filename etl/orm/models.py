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
    name = StringField(required=True)
    logo = StringField()
    category = ListField(field=StringField())

    def __str__(self):
        return self.name


class Show(Document):

    title = StringField(required=True)
    category = StringField()
    description = StringField()
    start = DateTimeField()
    end = DateTimeField()
    duration = FloatField()
    poster = StringField()
    channel_id = ReferenceField(Channel)

    def __str__(self):
        return self.title
