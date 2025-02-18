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
    timestamp = DateTimeField(default=timezone.now)

    def clean(self):
        if not self.text:
            raise ValueError("Message text cannot be empty.")
        if len(self.text.strip()) == 0:
            raise ValueError("Message text cannot be only whitespace.")


class Room(Document):
    participant_ids = ListField(IntField())
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)

    messages = EmbeddedDocumentListField(Message)

    meta = {
        "collection": "rooms",
        "indexes": [
            {
                "fields": ["$participant_ids"]
            },  # Ensure index is on participant_ids
        ],
    }

    def clean(self):

        if not self.participant_ids:
            raise ValueError("Participant IDs cannot be empty.")

        if len(self.participant_ids) != len(set(self.participant_ids)):
            raise ValueError("Participant IDs must be unique.")

        for message in self.messages:
            if message.sender_id not in self.participant_ids:
                raise ValueError(
                    f"Sender ID {message.sender_id} must be in participant_ids."
                )

        self.updated_at = timezone.now()
