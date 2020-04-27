from ..db import db

class Entity(db.Document):
    meta = {
        'collection': 'entities'
    }

    elements = db.DictField()