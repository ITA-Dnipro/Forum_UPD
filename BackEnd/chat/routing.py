import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")

from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r"ws/chat/", consumers.ChatConsumer.as_asgi()),
]
