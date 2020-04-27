from ..db import db


class NormUserIncident(db.Document):
    meta = {
        'collection': 'norm_userIncidents'
    }
    refId = db.IntField()
    title = db.StringField()
    normSources = db.ListField()
    normEvents = db.ListField()
    normEntities = db.ListField()
    normImpacts = db.ListField()