from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from mongoengine import connect, disconnect
import random
import string
import os
from chat.models import Room, Message
import unittest


class ConversationCreateViewTestCase(APITestCase):
    def setUp(self):
        """Set up users for authentication."""

        self.user1, _ = get_user_model().objects.get_or_create(
            email="testus123er6546123211412@example.com",
            defaults={
                "password": "testpassword",
                "name": "Test1",
                "surname": "User1",
            },
        )
        self.user2, _ = get_user_model().objects.get_or_create(
            email="testuser21275464567456@example.com",
            defaults={
                "password": "testpassword",
                "name": "Test2",
                "surname": "User2",
            },
        )
        self.url = reverse("chat:create_conversation")

    def tearDown(self):
        """Delete the users after tests."""
        self.user1.delete()
        self.user2.delete()

    def test_create_conversation(self):
        """Test creating a new conversation."""
        # Authenticate the user
        self.client.force_authenticate(user=self.user1)
        data = {
            "participant_ids": [
                self.user1.id,
                self.user2.id,
            ],
        }

        response = self.client.post(self.url, data, format="json")

        room = Room.objects.get(id=response.data["room_id"])
        room.delete()
        # Check the response status and message
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("room_id", response.data)
        self.assertEqual(response.data["message"], "Conversation was created")

    def test_create_conversation_unauthenticated(self):
        """Test creating a conversation without authentication."""
        data = {
            "participant_ids": [self.user1.id],
        }

        response = self.client.post(self.url, data, format="json")

        # Check for the correct status for unauthenticated requests
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MessageCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user1, _ = get_user_model().objects.get_or_create(
            email="testus123er6546123211412@example.com",
            defaults={
                "password": "testpassword",
                "name": "Test1",
                "surname": "User1",
            },
        )
        self.user2, _ = get_user_model().objects.get_or_create(
            email="testuser21275464567456@example.com",
            defaults={
                "password": "testpassword",
                "name": "Test2",
                "surname": "User2",
            },
        )
        self.url = reverse("chat:send_message")
        self.room = Room.objects.create(
            participant_ids=[self.user1.id, self.user2.id]
        )

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.room.delete()

    def test_send_message(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "room": str(self.room.id),
            "sender_id": self.user1.id,
            "text": "Hello, World!",
            "participant_ids": [self.user1.id, self.user2.id],
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"], "Message sent successfully."
        )

    def test_unauthenticated_request(self):
        """Test unauthenticated users cannot send messages."""
        data = {
            "sender_id": self.user1.id,
            "text": "Test message",
            "room": str(self.room.id),
            "participant_ids": [self.user1.id, self.user2.id],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sender_id_mismatch(self):
        """Test sender_id must match authenticated user."""
        self.client.force_authenticate(user=self.user1)
        data = {
            "sender_id": self.user2.id,  # Incorrect sender_id
            "text": "Test message",
            "room": str(self.room.id),
            "participant_ids": [self.user1.id, self.user2.id],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Sender ID does not match", response.data["message"])

    def test_invalid_data(self):
        """Test invalid data (e.g., missing text)."""
        self.client.force_authenticate(user=self.user1)
        data = {
            "sender_id": self.user1.id,
            "room": str(self.room.id),
            "participant_ids": [self.user1.id, self.user2.id],
            # Missing "text" field
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)


class MessageListViewTestCase(APITestCase):
    def setUp(self):
        self.user1, _ = get_user_model().objects.get_or_create(
            email="testus123er6546123211412@example.com",
            defaults={
                "password": "testpassword",
                "name": "Test1",
                "surname": "User1",
            },
        )
        self.user2, _ = get_user_model().objects.get_or_create(
            email="testuser21275464567456@example.com",
            defaults={
                "password": "testpassword",
                "name": "Test2",
                "surname": "User2",
            },
        )
        self.url = reverse("chat:send_message")
        self.room = Room.objects.create(
            participant_ids=[self.user1.id, self.user2.id]
        )
        self.message = Message.objects.create(
            room=self.room,
            sender_id=self.user1.id,
            text="Hello, World!",
        )

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.room.delete()
        self.message.delete()

    def test_get_messages(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            reverse("chat:get_messages", kwargs={"room_id": str(self.room.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("messages", response.data)
        self.assertEqual(len(response.data["messages"]), 1)
        self.assertEqual(response.data["messages"][0]["text"], "Hello, World!")

    def test_room_not_found(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            reverse("chat:get_messages", kwargs={"room_id": "fake-room-id"})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is not a valid", response.data["message"])

    def test_unauthenticated_request(self):
        response = self.client.get(
            reverse("chat:get_messages", kwargs={"room_id": str(self.room.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
