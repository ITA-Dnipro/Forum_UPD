from django.core.management.base import BaseCommand
from custom_auth.consumers import consume_role_updates

class Command(BaseCommand):
    help = "Starts the Kafka consumer for user role updates."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting Kafka consumer..."))
        consume_role_updates()
