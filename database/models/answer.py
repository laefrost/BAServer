from ..db import db

class Answer(db.Document):
    meta = {
        'collection': 'answers'
    }
    questionId = db.IntField()
    topicId = db.IntField()
    attributeId = db.IntField()