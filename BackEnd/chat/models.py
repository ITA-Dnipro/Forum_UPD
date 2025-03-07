from mongoengine import Document
from mongoengine.fields import (
    StringField,
    DateTimeField,
    IntField,
    ValidationError,
    SortedListField,
    ReferenceField,
)
from django.utils import timezone
from chat_notifications.signals import notification_signal
from .validators import custom_validator_that_escapes_xss
from django_cryptography.fields import encrypt
from utils.encryption_utils import encrypt_text, decrypt_text


class Room(Document):
    participant_ids = SortedListField(IntField(), required=True)
    created_at = DateTimeField(default=lambda: timezone.now())
    updated_at = DateTimeField(default=lambda: timezone.now())

    meta = {"collection": "rooms", "indexes": ["created_at"]}

    def clean(self):
        if not isinstance(self.participant_ids, list):
            raise ValidationError("participant_ids must be a list")

        if not all(
            isinstance(user_id, int) for user_id in self.participant_ids
        ):
            raise ValidationError("All participant IDs must be integers")

        if len(self.participant_ids) != len(set(self.participant_ids)):
            raise ValidationError("participant_ids contains duplicates")

        self.participant_ids = sorted(self.participant_ids)

        pipeline = [
            {
                "$match": {
                    "participant_ids": {"$all": self.participant_ids},
                    "$expr": {
                        "$eq": [
                            {"$size": "$participant_ids"},
                            len(self.participant_ids),
                        ]
                    },
                }
            },
            {"$limit": 1},
        ]

        existing_room = list(Room.objects.aggregate(pipeline))
        if existing_room:
            raise ValidationError(
                "A room with the same participants already exists."
            )

    def __str__(self):
        return f"Room created at {self.created_at}, participant_ids {self.participant_ids}"

    def __repl__(self):
        return f"Room created at {self.created_at}, participant_ids {self.participant_ids}"


class Message(Document):

    room = ReferenceField(Room, required=True)
    sender_id = IntField(required=True)
    text = StringField(
        required=True, validators=[custom_validator_that_escapes_xss]
    )
    timestamp = DateTimeField(default=lambda: timezone.now())
    meta = {
        "indexes": [
            "timestamp",
        ],
        "collection": "messages",
    }

    def clean(self):
        if not self.text:
            raise ValidationError("Message text cannot be empty.")
        if len(self.text.strip()) == 0:
            raise ValidationError("Message text cannot be only whitespace.")
        if not self.sender_id:
            raise AttributeError("Sender ID is required.")
        if self.sender_id not in self.room.participant_ids:
            raise ValidationError("Sender is not in the room")

    def save(self, *args, **kwargs):
        """Update the room's updated_at field when a new message is created."""
        if not self.pk:
            self.room.update(set__updated_at=timezone.now())
        self.text = encrypt_text(self.text)

        message = super().save(*args, **kwargs)
        notification_signal.send(
            sender=self.__class__,
            message=message,
            room=self.room,
            recipient_ids=[
                user_id
                for user_id in self.room.participant_ids
                if user_id != self.sender_id
            ],
            created=True,
        )
        return message

    def set_text(self, plain_text: str):
        self.text = encrypt_text(plain_text)

    # Custom method to get the decrypted text
    def get_text(self):
        return decrypt_text(self.text)
