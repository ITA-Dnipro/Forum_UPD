from rest_framework import serializers
from .models import Message, Room
from django.utils import timezone

from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    text = serializers.CharField(allow_blank=True, required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)
    conversation_id = serializers.CharField(required=False)


from rest_framework import serializers
from .models import Room, Message
from .serializers import MessageSerializer


class RoomSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(child=serializers.IntegerField())
    created_at = serializers.DateTimeField(default=timezone.now)
    updated_at = serializers.DateTimeField(default=timezone.now)
    messages = MessageSerializer(many=True, required=False)

    def create(self, validated_data):
        """
        Create and return a new `Room` instance, given the validated data.
        """
        print(f"created method: {validated_data}")
        messages_data = validated_data.pop("messages", [])
        room = Room.objects.create(**validated_data)

        # Create message instances and add them to the room
        for message_data in messages_data:
            Message.objects.create(room=room, **message_data)

        return room

    def update(self, instance, validated_data):
        """
        Update and return an existing `Room` instance, given the validated data.
        """
        messages_data = validated_data.pop("messages", [])

        # Update fields in the room instance
        instance.participant_ids = validated_data.get(
            "participant_ids", instance.participant_ids
        )
        instance.created_at = validated_data.get(
            "created_at", instance.created_at
        )
        instance.updated_at = validated_data.get(
            "updated_at", instance.updated_at
        )
        instance.save()

        for message_data in messages_data:
            Message.objects.update_or_create(room=instance, **message_data)

        return instance
