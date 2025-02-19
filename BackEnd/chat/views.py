from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer
from rest_framework import status
from .models import Room, Message
from rest_framework.permissions import IsAuthenticated, AllowAny


class CreateConversation(APIView):
    # permission_classes = [
    #     IsAuthenticated
    # ]  # Ensure only authenticated users can create a conversation

    def post(self, request, format=None):
        # Try to fetch the authenticated user's ID
        try:
            api_requested_sender_id = request.user.id
            print(f"Request sender ID: {api_requested_sender_id}")
        except AttributeError:
            return Response(
                {"message": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Deserialize the request data
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            participant_ids = sorted(request.data.get("participant_ids", []))

            # Ensure that the authenticated user is included in the participant_ids
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

            # Create and save the room (conversation)
            room = serializer.save()

            return Response(
                {"message": "Conversation was created"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            api_requested_sender_id = request.user.id
            print(f"request sender id: {api_requested_sender_id}")
        except AttributeError:
            return Response(
                {"message": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            conversation_id = serializer.validated_data["conversation_id"]
            message_text = serializer.validated_data["text"]
            sender_id = api_requested_sender_id  # Use authenticated user's ID as sender_id

            try:
                room = Room.objects.get(conversation_id=conversation_id)
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

            new_message = Message(sender_id=sender_id, text=message_text)
            room.update(push__messages=new_message)

            return Response(
                {"message": "Message sent successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMessages(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request, conversation_id, format=None):
        try:
            room = Room.objects.get(conversation_id=conversation_id)

            serializer = MessageSerializer(room.messages, many=True)

            return Response(
                {"messages": serializer.data}, status=status.HTTP_200_OK
            )

        except Room.DoesNotExist:
            return Response(
                {"message": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
