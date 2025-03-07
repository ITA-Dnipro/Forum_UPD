import os
from django.core.asgi import get_asgi_application
from itertools import chain

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")
django_asgi_app = get_asgi_application()

# Imports should be this way
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routing import chat_websocket_urlpatterns
from chat_notifications.routing import notification_websocket_urlpatterns
from authentication.authentication import JWTAuthMiddlewareStack

combined_websocket_urlpatterns = list(
    chain(chat_websocket_urlpatterns, notification_websocket_urlpatterns)
)
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddlewareStack(
            URLRouter(combined_websocket_urlpatterns)
        ),
    }
)
