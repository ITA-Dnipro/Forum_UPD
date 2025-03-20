from django.urls import re_path
from .consumer import NotificationConsumer

notification_websocket_urlpatterns = [
    re_path(r"ws/notifications/", NotificationConsumer.as_asgi()),
]
