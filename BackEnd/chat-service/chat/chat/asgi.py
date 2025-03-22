import os
from dotenv import load_dotenv
import mongoengine

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# 1️⃣ Завантаження змінних середовища
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat.settings")
load_dotenv()

# 2️⃣ Підключення до MongoDB перед імпортом моделей


print("✅ MongoDB connected!")

# 3️⃣ Створення ASGI-додатку
django_asgi_app = get_asgi_application()

# 4️⃣ Імпорт маршрутів тільки після підключення до Mongo
from chat_copy.routing import websocket_urlpatterns

# 5️⃣ Оголошення ProtocolTypeRouter
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
