from django.apps import AppConfig


class ChatNotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat_notifications"

    def ready(self):
        import chat_notifications.signals
