import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room = await self.get_or_create_room()
        print(f"room: {self.room}")
        # print header
        print(f'header: {self.scope["headers"]}')
        print(f'user: {self.scope["user"]}')
        print(f'type: {type(self.scope["user"])}')
        print(f'user_id: {self.scope["user"].id}')

        # Join room group
        await self.channel_layer.group_add(self.room_id, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.room_id,
            {"type": "chat_message", "message": text_data},
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def get_or_create_room(self):
        """Get or create a room with the given id"""
        try:
            room = Room.objects.get(id=self.room_id)
        except Room.DoesNotExist:
            room = Room.objects.create(id=self.room_id)

        return room
