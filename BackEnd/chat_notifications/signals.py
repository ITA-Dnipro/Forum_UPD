from django.dispatch import Signal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def create_notification(
    sender, message, room, recipient_ids, created, **kwargs
):

    if created:
        from chat_notifications.models import Notification

        # Create a new notification for each recipient
        for recipient_id in recipient_ids:
            notification = Notification.objects.create(
                recipient_id=recipient_id,
                message=message,
                room=room,
            )

            # Send the notification to the channel layer (WebSocket)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{recipient_id}",  # Unique group for each user
                {
                    "type": "send_notification",
                    "notification": f"New message from {message.sender_id}",
                },
            )


notification_signal = Signal()
notification_signal.connect(create_notification)
