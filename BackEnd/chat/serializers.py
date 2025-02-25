from rest_framework import serializers
from django.utils import timezone
from bson import ObjectId
import json
from .models import Message, Room


class RoomSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(child=serializers.IntegerField())
    created_at = serializers.DateTimeField(default=timezone.now)
    updated_at = serializers.DateTimeField(default=timezone.now)

    def create(self, validated_data):
        # Create a new Room instance
        return Room.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update an existing Room instance
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
        return instance

    def validate_participant_ids(self, value):
        """
        Custom validation to ensure participant_ids are unique and sorted.
        """
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "participant_ids contains duplicates"
            )

        if not all(isinstance(user_id, int) for user_id in value):
            raise serializers.ValidationError(
                "All participant IDs must be integers"
            )

        return sorted(value)


class MessageSerializer(serializers.Serializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    sender_id = serializers.IntegerField()
    text = serializers.CharField()
    timestamp = serializers.DateTimeField(default=timezone.now)

    def create(self, validated_data):
        # Create a new Message instance
        return Message.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update an existing Message instance
        instance.sender_id = validated_data.get(
            "sender_id", instance.sender_id
        )
        instance.text = validated_data.get("text", instance.text)
        instance.timestamp = validated_data.get(
            "timestamp", instance.timestamp
        )
        instance.save()
        return instance

    def validate_text(self, value):
        """
        Ensure that the message text is not empty or just whitespace.
        """
        if len(value) > 500:
            raise serializers.ValidationError(
                "Message text is too long. It should be no more than 500 characters."
            )
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError(
                "Message text cannot be empty or just whitespace."
            )
        return value

    def to_representation(self, instance):
        """
        Customize serialization to handle ObjectId fields properly.
        """
        representation = super().to_representation(instance)

        for field, value in representation.items():
            if isinstance(value, ObjectId):
                representation[field] = str(value)

        return representation
