from mongoengine import Document
from mongoengine.fields import (
    ReferenceField,
    IntField,
    BooleanField,
    DateTimeField,
    LazyReferenceField,
)
from django.utils import timezone
from chat.models import Message, Room


class Notification(Document):
    recipient_id = IntField(required=True)
    message = ReferenceField(Message, required=True, reverse_delete_rule=2)
    is_read = BooleanField(default=False)
    room = ReferenceField(Room, required=True, reverse_delete_rule=2)
    created_at = DateTimeField(default=lambda: timezone.now())

    meta = {
        "collection": "notifications",
        "indexes": ["recipient_id", "is_read", "created_at"],
    }

    def __str__(self):
        return f"Notification for {self.recipient_id} - Read: {self.is_read}"
