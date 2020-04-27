from ..db import db

class Impact(db.Document):
    meta = {
        'collection': 'impacts'
    }
    elements = db.DictField()