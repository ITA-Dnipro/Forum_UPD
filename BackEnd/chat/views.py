from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat
from .serializers import MessageSerializer


# Create a new message (POST)
class MessageCreate(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("send from front")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve all messages (GET)
class MessageList(APIView):
    def get(self, request):
        chats = Chat.objects.all()
        serializer = MessageSerializer(chats, many=True)
        return Response(serializer.data)


# Retrieve a single message by id (GET)
class MessageDetail(APIView):
    def get(self, request, pk):
        try:
            chat = Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MessageSerializer(chat)
        return Response(serializer.data)


# Update a message (PUT)
class MessageUpdate(APIView):
    def put(self, request, pk):
        try:
            chat = Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MessageSerializer(chat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete a message (DELETE)
class MessageDelete(APIView):
    def delete(self, request, pk):
        try:
            chat = Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
