import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    # async def connect(self):
    #     self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
    #     self.room_group_name = f"chat_{self.room_name}"

    #     try:
    #         # Join room group
    #         await self.channel_layer.group_add(
    #             self.room_group_name, self.channel_name
    #         )
    #         await self.accept()
    #     except Exception as e:
    #         logger.error(f"Failed to join room group: {e}")
    #         await self.close()

    # async def disconnect(self, close_code):
    #     try:
    #         await self.channel_layer.group_discard(
    #             self.room_group_name, self.channel_name
    #         )
    #     except Exception as e:
    #         logger.warning(f"Failed to discard from room group: {e}")

    # async def receive(self, text_data):
    #     try:
    #         text_data_json = json.loads(text_data)
    #         message = text_data_json.get("message")
    #         if message:
    #             await self.channel_layer.group_send(
    #                 self.room_group_name,
    #                 {"type": "chat.message", "message": message},
    #             )
    #         else:
    #             logger.warning("Received message without 'message' key")
    #     except json.JSONDecodeError:
    #         logger.warning("Invalid JSON received")
    #     except Exception as e:
    #         logger.error(f"Error while processing received message: {e}")

    # async def chat_message(self, event):
    #     message = event.get("message")
    #     if message:
    #         try:
    #             await self.send(text_data=json.dumps({"message": message}))
    #         except Exception as e:
    #             logger.error(f"Failed to send message: {e}")
    #     else:
    #         logger.warning("Received event without 'message' key")
    pass
