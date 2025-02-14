from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, DateTimeField, ReferenceField, ListField,
    EmbeddedDocumentListField, EmbeddedDocumentField, IntField
)
from django.utils import timezone

class Message(EmbeddedDocument):
    
    sender_id = IntField(required=True)  
    text = StringField()
    timestamp = DateTimeField(default=timezone.now)


class Room(Document):

    participant_ids = ListField(IntField())
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)

    messages = EmbeddedDocumentListField(Message)

    meta = {
        "collection": "rooms",
        "indexes": [
            {"fields": ["$participant_ids"]},  #added a "$" sign to explicitly specify multiKey.
        ],
    }