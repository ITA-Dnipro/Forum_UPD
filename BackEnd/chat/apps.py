from django.apps import AppConfig
import mongoengine

class ChatConfig(AppConfig):
    name = "chat"

    def ready(self):
        
        from . import models
        models.Room.ensure_indexes()