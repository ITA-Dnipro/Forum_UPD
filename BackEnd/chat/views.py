from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer
from rest_framework import status
from .models import Room, Message
from rest_framework.permissions import IsAuthenticated


class CreateConversation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            api_requested_sender_id = request.user.id
        except AttributeError:
            return Response(
                {"message": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            participant_ids = sorted(request.data.get("participant_ids", []))

            if api_requested_sender_id not in participant_ids:
                return Response(
                    {
                        "message": "You must be a participant in the conversation."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            existing_room = Room.objects.filter(
                participant_ids=participant_ids
            ).first()

            if existing_room:
                return Response(
                    {
                        "message": "A room with this participant pair already exists."
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            serializer.save()
            return Response(
                {"message": "Conversation was created"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            api_requested_sender_id = request.user.id
        except AttributeError:
            return Response(
                {"message": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = MessageSerializer(data=request.data)
        participant_ids = request.data["participant_ids"]
        if serializer.is_valid():
            sender_id = api_requested_sender_id

            try:
                room = Room.objects.get(participant_ids=participant_ids)
            except Room.DoesNotExist:
                return Response(
                    {"message": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if sender_id not in room.participant_ids:
                return Response(
                    {
                        "message": "Sender is not a participant of this conversation."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer.save()

            return Response(
                {"message": "Message sent successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMessages(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            room = Room.objects.get(id=request.query_params.get("room_id"))
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
