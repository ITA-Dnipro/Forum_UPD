from django.test import TestCase
from mongoengine import connect, disconnect, ValidationError
from .models import Room, Message
from django.utils import timezone
import os
import random
import string
from unittest import skip


class TestRoomMessage(TestCase):

    def setUp(self):
        # Disconnect any existing connections first
        disconnect(alias="default")

        # Create a random test database name
        test_db_name = "test_" + "".join(
            random.choices(string.ascii_lowercase, k=8)
        )

        # Get MongoDB credentials from environment variables
        db_username = os.getenv("MONGO_USERNAME")
        db_password = os.getenv("MONGO_PASSWORD")
        db_host = os.getenv("MONGO_HOST")
        db_port = int(os.getenv("MONGO_PORT"))
        db_auth_source = os.getenv("MONGO_AUTHENTICATION_SOURCE")

        # Connect to the MongoDB instance using the environment variables
        connect(
            db=test_db_name,
            username=db_username,
            password=db_password,
            host=db_host,
            port=db_port,
            authentication_source=db_auth_source,
            alias="default",
        )

    def tearDown(self):
        """Disconnect from the database after each test"""
        disconnect(alias="default")

    def test_create_room(self):
        """Test creating a room successfully"""
        room = Room(participant_ids=[1, 2, 3])
        room.save()
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(room.participant_ids, [1, 2, 3])

    def test_create_room_with_duplicates(self):
        """Test creating a room with duplicate participants should raise an error"""

        with self.assertRaises(ValidationError) as context:
            Room(participant_ids=[1, 1, 2]).save()
        self.assertIn(
            "participant_ids contains duplicates", str(context.exception)
        )

    def test_create_duplicate_room(self):
        """Test creating a room with the same participants should raise an error"""
        Room(participant_ids=[1, 2, 3]).save()
        with self.assertRaises(ValidationError) as context:
            Room(participant_ids=[1, 2, 3]).save()
        self.assertIn(
            "A room with the same participants already exists.",
            str(context.exception),
        )

    def test_create_message(self):
        """Test creating a message successfully"""
        room = Room(participant_ids=[1, 2, 3])
        room.save()
        message = Message(room=room, sender_id=1, text="Hello")
        message.save()
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.text, "Hello")
        self.assertEqual(message.room, room)

    def test_message_from_non_participant(self):
        """Test that a message cannot be sent by a non-participant"""
        room = Room(participant_ids=[1, 2, 3])
        room.save()

        with self.assertRaises(ValidationError) as context:
            Message(room=room, sender_id=4, text="Hello").save()
        self.assertIn("Sender is not in the room", str(context.exception))

    def test_message_empty_text(self):
        """Test that a message cannot be sent with empty text"""
        room = Room(participant_ids=[1, 2, 3])
        room.save()

        with self.assertRaises(ValidationError) as context:
            Message(room=room, sender_id=1, text="").save()
        self.assertIn("Message text cannot be empty.", str(context.exception))

    def test_message_whitespace_text(self):
        """Test that a message cannot be sent with only whitespace text"""
        room = Room(participant_ids=[1, 2, 3])
        room.save()

        with self.assertRaises(ValidationError) as context:
            Message(room=room, sender_id=1, text="   ").save()
        self.assertIn(
            "Message text cannot be only whitespace.", str(context.exception)
        )

    def test_room_updated_at_on_message(self):
        """Test that the `updated_at` field of the room is updated when a new message is sent"""
        room = Room(participant_ids=[1, 2, 3])
        room.save()

        old_updated_at = room.updated_at.astimezone(timezone.utc).replace(
            tzinfo=None
        )

        message = Message(room=room, sender_id=1, text="First message")
        message.save()

        room.reload()
        self.assertTrue(room.updated_at.replace(tzinfo=None) > old_updated_at)
