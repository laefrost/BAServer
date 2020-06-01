from mongoengine import EmbeddedDocumentField

from ..db import db

class SourceNew(db.Document):
    meta = {
        'collection': 'sources'
    }
    id = db.IntField()
    elements: db.ListField()