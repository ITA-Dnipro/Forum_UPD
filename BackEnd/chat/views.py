from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer
from rest_framework import status
from .models import Room, Message

# from rest_framework import authentication, permissions
# from django.contrib.auth.models import User


class CreateConversation(APIView):

    def post(self, request, format=None):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():

            participant_ids = sorted(request.data.get("participant_ids", []))

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

            room = serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendMessage(APIView):
    def post(self, request, format=None):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            conversation_id = serializer.validated_data["conversation_id"]
            message_text = serializer.validated_data["text"]
            sender_id = serializer.validated_data["sender_id"]

            try:
                room = Room.objects.get(conversation_id=conversation_id)
            except Room.DoesNotExist:
                return Response(
                    {"message": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Check if sender_id is in the participant_ids of the room
            if sender_id not in room.participant_ids:
                return Response(
                    {
                        "message": "Sender is not a participant of this conversation."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create the new message
            new_message = Message(sender_id=sender_id, text=message_text)

            # Append the new message to the room's messages
            room.update(push__messages=new_message)

            return Response(
                {"message": "Message sent successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMessages(APIView):
    def get(self, request, conversation_id, format=None):
        try:
            # Retrieve the room (conversation) by conversation_id
            room = Room.objects.get(conversation_id=conversation_id)

            # If the room exists, serialize the messages
            serializer = MessageSerializer(room.messages, many=True)

            # Return the serialized messages
            return Response(
                {"messages": serializer.data}, status=status.HTTP_200_OK
            )

        except Room.DoesNotExist:
            # If the room (conversation) does not exist, return a 404 error
            return Response(
                {"message": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
