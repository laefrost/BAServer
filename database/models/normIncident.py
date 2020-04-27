from ..db import db


class NormIncident(db.Document):
    meta = {
        'collection': 'norm_incidents'
    }
    refId = db.IntField()
    title = db.StringField()
    normSources = db.ListField()
    normEvents = db.ListField()
    normEntities = db.ListField()
    normImpacts = db.ListField()
