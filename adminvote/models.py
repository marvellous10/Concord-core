from mongoengine import *

class VotingDB(Document):
    session_name= StringField(required=True)
    voting_code= StringField(required=True)
    open_session= BooleanField(default=False)
    allowed_phone_numbers = ListField(required=True)
    candidates_voted = ListField()
    positions = ListField(required=True)
    
    meta = {
        'collection': 'VotingDB'
    }