import json

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

    oid = IntField()
    name = StringField(required=True)
    logo = StringField()
    category = ListField(field=StringField())

    def __str__(self):
        return self.name

    def json(self) -> str:
        return json.dumps(
            {
                "oid": self.oid,
                "name": self.name,
                "logo": self.logo,
                "category": self.category,
            }
        )


class Show(Document):

    title = StringField()
    category = StringField()
    description = StringField()
    start_dt = DateTimeField()
    end_dt = DateTimeField()
    start_ts = IntField()
    end_ts = IntField()
    duration = FloatField()
    poster = StringField()
    channel = ReferenceField(Channel, default=None)

    def __str__(self):
        return self.title

    def json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "category": self.category,
                "description": self.description,
                "start_dt": self.start_dt,
                "end_dt": self.end_dt,
                "start_ts": self.start_ts,
                "end_ts": self.end_ts,
                "duration": self.duration,
                "poster": self.poster,
            }
        )

    def update_channel(self, channel: Channel):
        self.channel = channel

    meta = {
        "indexes": ["start_ts"],
        "ordering": ["-start_ts"],
    }
