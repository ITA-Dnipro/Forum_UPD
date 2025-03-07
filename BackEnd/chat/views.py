import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer
from rest_framework import status
from .models import Room, Message
from rest_framework.permissions import IsAuthenticated
from forum.pagination import ForumPagination
from django_ratelimit.decorators import ratelimit

# Set up logging
logger = logging.getLogger(__name__)


class ConversationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True)
    def post(self, request, format=None):
        logger.info(
            "Conversation creation requested by user %s", request.user.id
        )

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            logger.info(
                "Conversation created successfully with room ID: %s", room.id
            )
            return Response(
                {
                    "message": "Conversation was created",
                    "room_id": str(room.id),
                },
                status=status.HTTP_201_CREATED,
            )

        logger.warning(
            "Failed to create conversation. Errors: %s", serializer.errors
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageSendView(APIView):
    permission_classes = [IsAuthenticated]

    @ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True)
    def post(self, request, format=None):
        api_requested_sender_id = request.user.id
        logger.info(
            "Message send requested by user %s", api_requested_sender_id
        )

        if api_requested_sender_id != request.data["sender_id"]:
            logger.warning(
                "Sender ID mismatch: user %s tried to send a message with sender_id %s",
                api_requested_sender_id,
                request.data["sender_id"],
            )
            return Response(
                {
                    "message": "Sender ID does not match the authenticated user."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                "Message sent successfully by user %s", api_requested_sender_id
            )
            return Response(
                {"message": "Message sent successfully."},
                status=status.HTTP_201_CREATED,
            )

        logger.warning("Failed to send message. Errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = [ForumPagination]

    @ratelimit(key="user_or_ip", rate="5/m", method="GET", block=True)
    def get(self, request, room_id, format=None):
        logger.info(
            "Message list requested for room %s by user %s",
            room_id,
            request.user.id,
        )

        try:
            room = Room.objects.get(id=room_id)
            messages = Message.objects.filter(room=room).order_by("timestamp")
            serializer = MessageSerializer(messages, many=True)
            logger.info(
                "Successfully retrieved %d messages for room %s",
                len(messages),
                room_id,
            )
            return Response(
                {"messages": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Room.DoesNotExist:
            logger.warning("Room %s not found", room_id)
            return Response(
                {"message": "Room not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(
                "Error occurred while retrieving messages for room %s: %s",
                room_id,
                str(e),
            )
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
