from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("trying to connect")
        self.room_group_name = f'notifications_{self.scope["user"].id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from room group
    async def send_notification(self, event):
        notification = event["notification"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"notification": notification}))
