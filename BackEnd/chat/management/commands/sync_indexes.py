# chat/management/commands/add_test_data.py
from django.core.management.base import BaseCommand
from datetime import datetime
from chat.models import Room, Message

class Command(BaseCommand):
    help = 'Вставка тестових даних для моделі Room'

    def handle(self, *args, **options):
        self.stdout.write("Створення тестових даних для моделі Room...")

        try:
            room = Room(
                participant_ids=[1, 2, 3],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            room.messages.append(Message(sender_id=1, text="Привіт, як справи?", timestamp=datetime.utcnow()))
            room.messages.append(Message(sender_id=2, text="Все добре, дякую!", timestamp=datetime.utcnow()))
            room.save()

            self.stdout.write(self.style.SUCCESS(f"Тестова кімната створена з id: {room.id}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Помилка під час створення кімнати: {e}"))
