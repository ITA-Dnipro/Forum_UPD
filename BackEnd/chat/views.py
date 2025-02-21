from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import RoomSerializer, MessageSerializer
from .models import Room, Message


def error_response(message, status_code):
    """Helper function to return consistent error responses."""
    return Response({"message": message}, status=status_code)


class CreateConversation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        participant_ids = sorted(request.data.get("participant_ids", []))

        if request.user.id not in participant_ids:
            return error_response(
                "You must be a participant in the conversation.",
                status.HTTP_403_FORBIDDEN,
            )

        # Check if a room with the same participants already exists
        if Room.objects.filter(participant_ids=participant_ids).exists():
            return error_response(
                "A room with this participant pair already exists.",
                status.HTTP_409_CONFLICT,
            )

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Conversation was created"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        participant_ids = request.data.get("participant_ids")

        if not participant_ids:
            return error_response(
                "Participant IDs are required.", status.HTTP_400_BAD_REQUEST
            )

        # Ensure room exists with given participants
        room = Room.objects.filter(participant_ids=participant_ids).first()
        if not room:
            return error_response(
                "Conversation not found.", status.HTTP_404_NOT_FOUND
            )

        if request.user.id not in room.participant_ids:
            return error_response(
                "Sender is not a participant of this conversation.",
                status.HTTP_403_FORBIDDEN,
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Message sent successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMessages(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        room = get_object_or_404(Room, id=request.query_params.get("room_id"))

        if request.user.id not in room.participant_ids:
            return error_response(
                "You are not a participant of this conversation.",
                status.HTTP_403_FORBIDDEN,
            )

        messages = Message.objects.filter(room=room).order_by("timestamp")
        serializer = MessageSerializer(messages, many=True)
        return Response(
            {"messages": serializer.data}, status=status.HTTP_200_OK
        )
