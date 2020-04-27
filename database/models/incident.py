from ..db import db

class Incident(db.Document):
    meta = {
        'collection': 'predef_incidents'
    }
    myId = db.IntField()
    idCount = db.IntField()
    impact = db.StringField()
    sources = db.ListField()
    entities = db.ListField()
    events = db.ListField()
    impacts = db.ListField()
    #email= db.StringField()
    #description= db.StringField()
    #technicalData= db.StringField()
    title= db.StringField()
    #time = db.StringField()