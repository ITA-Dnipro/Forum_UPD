import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from . import consumers
from django.urls import re_path


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")


websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
