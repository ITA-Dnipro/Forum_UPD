import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from .serializers import MessageSerializer
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = str(self.scope["url_route"]["kwargs"]["room_id"])

        # Check if user is authenticated before proceeding
        if not self.scope["user"].is_authenticated:
            logger.warning(f"User {self.scope['user']} is not authenticated.")
            await self.close()
            return

        # Get or create room
        self.room = await self.get_or_create_room()

        if not self.room:
            logger.error(
                f"Room with id {self.room_id} could not be found or created."
            )
            await self.close()
            return

        if self.channel_layer is None:
            logger.error("channel_layer is not configured properly.")
            await self.close()
            return

        # Add to the channel group for broadcasting
        await self.channel_layer.group_add(self.room_id, self.channel_name)
        await self.accept()
        logger.info(
            f"User {self.scope['user']} connected to room {self.room_id}."
        )

    async def receive(self, text_data):
        if self.room is None:
            logger.error("Room is None, cannot send message.")
            await self.close()
            return

        # Serialize and validate the incoming message
        try:
            # Parse the incoming text data as JSON
            data = json.loads(text_data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in incoming message.")
            return
        serializer = MessageSerializer(
            data={
                "room": self.room.id,
                "sender_id": self.scope["user"].id,
                "text": data.get("text"),
            }
        )

        if serializer.is_valid():
            await self.save_message(serializer)
        else:
            logger.error(f"MessageSerializer error: {serializer.errors}")

        # Send the message to the channel group for broadcasting
        await self.channel_layer.group_send(
            self.room_id,
            {
                "type": "chat_message",
                "message": text_data,
                "sender_id": self.scope["user"].id,
            },
        )

    @database_sync_to_async
    def get_or_create_room(self):
        """Get or create a room with the given id."""
        try:
            room = Room.objects.get(id=self.room_id)
            if self.scope["user"].id not in room.participant_ids:
                raise PermissionDenied(
                    f"User {self.scope['user'].id} is not a participant of room {self.room_id}"
                )
            return room
        except Room.DoesNotExist:
            logger.error(f"Room with id {self.room_id} does not exist.")
            return None

    @database_sync_to_async
    def save_message(self, serializer):
        """Save the message to the database."""
        if serializer.is_valid():
            serializer.save()

    async def chat_message(self, event):
        """Send the message to the client."""
        message = event["message"]
        sender_id = event["sender_id"]

        # Avoid sending the message back to the sender
        try:
            if sender_id != self.scope["user"].id:
                await self.send(
                    text_data=json.dumps(
                        {"message": message, "sender_id": sender_id}
                    )
                )
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

    async def disconnect(self, close_code):
        """Handle the disconnect event."""
        if self.channel_layer is not None:
            try:
                await self.channel_layer.group_discard(
                    self.room_id, self.channel_name
                )
            except Exception as e:
                logger.error(f"Error in group_discard: {e}")

        logger.info(
            f"User {self.scope['user']} disconnected from room {self.room_id}."
        )
        await self.close()
