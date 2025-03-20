from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer
from rest_framework import status
from .models import Room, Message
from rest_framework.permissions import IsAuthenticated
from chat.pagination import ChatPagination


class ConversationCreateView(APIView):
    def post(self, request, format=None):
        print("hello there")
        print(request.data)
        print(f"Request payload: {request}")
        print(f"request headers: {request.headers}")
        try:
            serializer = RoomSerializer(data=request.data)
            if serializer.is_valid():
                room = serializer.save()
                print("Saved room")
                print(f"Room ID: {room.id}")
                response = Response(
                    {
                        "message": "Conversation was created",
                        "room_id": str(room.id),
                    },
                    status=status.HTTP_201_CREATED,
                    content_type="application/json",
                )
                print(f"Response: {response}")
                print(f"Response status: {response.status_code}")
                print(f"Response data: {response.data}")
                print(f"Response headers: {response.headers}")
                return response
        except Exception as e:
            print(f"Error123: {str(e)}")
            return Response(
                {"message": "An error occurred."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageSendView(APIView):

    def post(self, request, format=None):

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Message sent successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageListView(APIView):
    pagination_class = [ChatPagination]

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
