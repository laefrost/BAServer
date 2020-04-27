from ..db import db

class Question(db.Document):
    meta = {
        'collection': 'questions'
    }
    text = db.StringField()
    questionId = db.IntField()