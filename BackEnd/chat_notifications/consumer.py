from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from channels.exceptions import ChannelFull

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        if not self.scope["user"].is_authenticated:
            logger.warning("Unauthenticated user attempted to connect.")
            await self.close()
            return

        self.room_group_name = f'notifications_{self.scope["user"].id}'

        if self.channel_layer is None:
            logger.error("channel_layer is not configured properly.")
            await self.close()
            return

        try:
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            logger.info(
                f"User {self.scope['user'].id} connected to notifications."
            )
        except ValueError as e:
            logger.error(f"Invalid value when adding user to group: {str(e)}")
            await self.close()
        except RuntimeError as e:
            logger.error(f"Runtime error when adding user to group: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.channel_layer is not None:
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )
                logger.info(
                    f"User {self.scope['user'].id} disconnected from notifications."
                )
            except KeyError as e:
                logger.error(f"KeyError in group_discard: {str(e)}")
            except RuntimeError as e:
                logger.error(f"Runtime error in group_discard: {str(e)}")

    async def send_notification(self, event):
        """Send notification to the WebSocket client."""
        try:
            notification = event.get(
                "notification", "No notification data provided"
            )
            await self.send(
                text_data=json.dumps({"notification": notification})
            )
        except json.JSONDecodeError as e:
            logger.error(
                f"JSON encoding error while sending notification: {str(e)}"
            )
        except ChannelFull as e:
            logger.error(f"Channel layer is full, message dropped: {str(e)}")
        except ConnectionError as e:
            logger.error(
                f"Connection error while sending notification: {str(e)}"
            )
