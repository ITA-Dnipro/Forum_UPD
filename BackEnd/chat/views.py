from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer
from rest_framework import status
from .models import Room, Message
from rest_framework.permissions import IsAuthenticated
from forum.pagination import ForumPagination


class ConversationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(
                {
                    "message": "Conversation was created",
                    "room_id": str(room.id),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        api_requested_sender_id = request.user.id

        if api_requested_sender_id != request.data["sender_id"]:
            return Response(
                {
                    "message": "Sender ID does not match the authenticated user."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Message sent successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = [ForumPagination]

    def get(self, request, room_id, format=None):
        try:
            room = Room.objects.get(id=room_id)
            messages = Message.objects.filter(room=room).order_by("timestamp")
            serializer = MessageSerializer(messages, many=True)
            return Response(
                {"messages": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Room.DoesNotExist:
            return Response(
                {"message": "Room not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
