from django.core.management.base import BaseCommand
from custom_auth.consumers import process_role_update_message

class Command(BaseCommand):
    help = "Consume user role update messages from Kafka"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Kafka consumer for role updates...")
        process_role_update_message()
