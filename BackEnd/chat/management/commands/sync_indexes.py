# chat/management/commands/sync_indexes.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from chat.models import Room, Message

class Command(BaseCommand):
    help = 'Вставка тестових даних для моделі Room'

    def handle(self, *args, **options):
        self.stdout.write("Створення тестових даних для моделі Room...")

        try:
            room = Room(
                participant_ids=[1, 2, 3],
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

            room.messages.append(Message(sender_id=1, text="Привіт, як справи?", timestamp=timezone.now()))
            room.messages.append(Message(sender_id=2, text="Все добре, дякую!", timestamp=timezone.now()))
            room.save()

            self.stdout.write(self.style.SUCCESS(f"Тестова кімната створена з id: {room.id}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Помилка під час створення кімнати: {e}"))
