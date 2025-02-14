from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Message
from .serializers import MessageSerializer

# Template views
def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})

# API views
class MessageList(APIView):
    def get(self, request):
        chats = Message.objects.all()
        serializer = MessageSerializer(chats, many=True)
        return Response(serializer.data)

class MessageDetail(APIView):
    def get(self, request, pk):
        try:
            chat = Message.objects.get(pk=pk)
        except Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MessageSerializer(chat)
        return Response(serializer.data)

class MessageUpdate(APIView):
    def put(self, request, pk):
        try:
            chat = Message.objects.get(pk=pk)
        except Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MessageSerializer(chat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageDelete(APIView):
    def delete(self, request, pk):
        try:
            chat = Message.objects.get(pk=pk)
        except Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)