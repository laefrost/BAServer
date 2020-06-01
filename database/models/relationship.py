from ..db import db

class Relationship(db.Document):
    meta = {
        'collection': 'relationship'
    }
    questionId = db.IntField()
    topicId = db.IntField()
    attributeId = db.StringField()
    #parentAttrId = db.IntField()