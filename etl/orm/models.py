from mongoengine import (
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    FloatField,
    IntField,
    ListField,
    StringField,
)

import pendulum


class Show(EmbeddedDocument):

    title = StringField()
    category = StringField()
    description = StringField()
    start_dt = DateTimeField()
    end_dt = DateTimeField()
    start_ts = IntField()
    end_ts = IntField()
    duration = FloatField()
    poster = StringField()
    oid = IntField()

    def __str__(self):
        return self.title


class Channel(Document):

    oid = IntField()
    name = StringField(required=True)
    logo = StringField()
    category = ListField(field=StringField())
    shows = EmbeddedDocumentListField(Show)

    def __str__(self):
        return f"{self.name} with ({len(self.shows)}) shows"


class Date(Document):

    date_tz = DateTimeField()
    timestamp = IntField()
    weekday = StringField()
    month = StringField()
    day = IntField()

    def __str__(self):
        return self.formatted
