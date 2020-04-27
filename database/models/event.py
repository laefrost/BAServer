from ..db import db

class Event(db.Document):
    meta = {
        'collection': 'events'
    }

    elements = db.DictField()