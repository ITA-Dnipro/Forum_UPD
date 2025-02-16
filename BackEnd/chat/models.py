from mongoengine import Document, EmbeddedDocument, ValidationError
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
    text = StringField()
    timestamp = DateTimeField(default=timezone.now)


class Room(Document):
    participant_ids = ListField(IntField(), required=True)
    conversation_id = StringField(
        unique=True, required=True
    )  # унікальний ключ
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)
    messages = EmbeddedDocumentListField(Message, default=list)

    meta = {
        "collection": "rooms",
        "indexes": [
            "conversation_id",
        ],
    }

    def save(self, *args, **kwargs):
        # Сортуємо ID для унікальності незалежно від порядку
        if self.participant_ids:
            self.participant_ids = sorted(self.participant_ids)
            self.conversation_id = "_".join(
                str(i) for i in self.participant_ids
            )

        # Перевіряємо наявність кімнати з таким ключем
        if Room.objects(conversation_id=self.conversation_id).first():
            raise ValidationError(
                "A room with this participant pair already exists."
            )

        self.updated_at = timezone.now()
        return super(Room, self).save(*args, **kwargs)
