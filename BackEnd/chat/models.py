from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    DateTimeField,
    ListField,
    EmbeddedDocumentListField,
    IntField,
)
from django.utils import timezone


class Message(EmbeddedDocument):
    sender_id = IntField(required=True)
    text = StringField(required=True)
    timestamp = DateTimeField(default=lambda: timezone.now())

    def clean(self):
        if not self.text:
            raise ValueError("Message text cannot be empty.")
        if len(self.text.strip()) == 0:
            raise ValueError("Message text cannot be only whitespace.")


class Room(Document):
    participant_ids = ListField(IntField(), required=True)
    created_at = DateTimeField(default=lambda: timezone.now())
    updated_at = DateTimeField(default=lambda: timezone.now())

    messages = EmbeddedDocumentListField(Message)

    meta = {
        "collection": "rooms",
        "indexes": [
            {"fields": ["$participant_ids"]}, 
            {"fields": ["messages.timestamp"]}, 
        ],
    }

    def clean(self):
        if not isinstance(self.participant_ids, list):
            raise ValueError("participant_ids must be a list")

        if not all(
            isinstance(user_id, int) for user_id in self.participant_ids
        ):
            raise ValueError("All participant IDs must be integers")

    def add_message(self, sender_id, text):

        if sender_id not in self.participant_ids:
            raise ValueError(
                f"Sender ID {sender_id} is not a participant in this room"
            )

        message = Message(sender_id=sender_id, text=text)
        self.messages.append(message)
        self.updated_at = timezone.now()

        self.save()
