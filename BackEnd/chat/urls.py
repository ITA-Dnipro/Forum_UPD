from django.urls import path
from .views import (
    MessageList,
    MessageCreate,
    MessageDetail,
    MessageUpdate,
    MessageDelete,
)

app_name = "chat"
urlpatterns = [
    path(
        "chats/", MessageList.as_view(), name="message-list"
    ),  # List all messages
    path(
        "chats/create/", MessageCreate.as_view(), name="message-create"
    ),  # Create new message
    path(
        "chats/<int:pk>/", MessageDetail.as_view(), name="message-detail"
    ),  # Get a specific message by id
    path(
        "chats/<int:pk>/update/",
        MessageUpdate.as_view(),
        name="message-update",
    ),  # Update a message
    path(
        "chats/<int:pk>/delete/",
        MessageDelete.as_view(),
        name="message-delete",
    ),  # Delete a message
]
