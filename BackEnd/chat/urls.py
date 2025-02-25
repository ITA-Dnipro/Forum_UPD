from django.urls import path
from .views import ConversationCreateView, MessageSendView, MessageListView

app_name = "chat"


urlpatterns = [
    path(
        "conversations/",
        ConversationCreateView.as_view(),
        name="create_conversation",
    ),
    path("messages/", MessageSendView.as_view(), name="send_message"),
    path(
        "conversations/<str:room_id>/history/",
        MessageListView.as_view(),
        name="get_messages",
    ),
]
