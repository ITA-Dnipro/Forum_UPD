import os
from . import consumers
from django.urls import re_path


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")


chat_websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
