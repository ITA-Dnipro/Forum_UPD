from django.urls import path
from .views import CreateConversation, SendMessage, GetMessages

app_name = "chat"


urlpatterns = [
    path("conversations/", CreateConversation.as_view()),
    path("messages/", SendMessage.as_view()),
    path(
        "conversations/<str:conversation_id>/messages/",
        GetMessages.as_view(),
        name="get_messages",
    ),
]
