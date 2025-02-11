from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, DateTimeField, ReferenceField, ListField,
    EmbeddedDocumentListField, EmbeddedDocumentField, IntField
)
from datetime import datetime

class Message(EmbeddedDocument):
    
    sender_id = IntField(required=True)  
    text = StringField()
    timestamp = DateTimeField(default=datetime.utcnow)


class Room(Document):

    participant_ids = ListField(IntField())
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    messages = EmbeddedDocumentListField(Message)

    meta = {
        "collection": "rooms",
        "indexes": [
            {"fields": ["participant_ids"]},  
        ],
    }