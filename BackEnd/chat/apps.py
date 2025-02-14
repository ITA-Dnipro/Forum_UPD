from django.apps import AppConfig
import mongoengine
import logging

logger = logging.getLogger(__name__)

class ChatConfig(AppConfig):
    name = "chat"

    def ready(self):
        try:

            from . import models
            models.Room.ensure_indexes()
        except Exception as e:
            logger.error(f"Error ensuring indexes for Room: {e}")