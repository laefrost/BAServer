from ..db import db

class SourceNew(db.Document):
    meta = {
        'collection': 'sources'
    }
    elements: db.ListField()