from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factories import UserFactory
from profiles.models import CustomUser
from utils.dump_response import dump  # noqa

from django.urls import reverse


class UserRegistrationAPITests(APITestCase):
    def setUp(self):
        patcher = patch(
            "authentication.serializers.verify_recaptcha", return_value=True
        )
        self.mock_verify_recaptcha = patcher.start()
        self.addCleanup(patcher.stop)

        self.user = UserFactory(email="test@test.com")

    def test_register_user_yurosoba_successful(self):
        url = reverse('authentication:register')
        response = self.client.post(
            url,
            data={
                "email": "jane@test.com",
                "password": "Test12!34",
                "re_password": "Test12!34",
                "name": "Jane",
                "surname": "Smith",
                "captcha": "dummy_captcha",
                "company": {
                    "name": "My Company",
                    "is_registered": True,
                    "is_startup": False,
                    "is_fop": False,
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {
                "name": "Jane",
                "surname": "Smith",
            },
            response.json(),
        )
        user = CustomUser.objects.get(email="jane@test.com")
        self.assertEqual(user.email, "jane@test.com")


    def test_register_user_fop_successful(self):
        url = reverse('authentication:register')
        response = self.client.post(
            url,
            data={
                "email": "jane@test.com",
                "password": "Test12!34",
                "re_password": "Test12!34",
                "name": "Jane",
                "surname": "Smith",
                "captcha": "dummy_captcha",
                "company": {
                    "name": "My Company",
                    "is_registered": True,
                    "is_startup": False,
                    "is_fop": True,
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {
                "name": "Jane",
                "surname": "Smith",
            },
            response.json(),
        )
        user = CustomUser.objects.get(email="jane@test.com")
        self.assertEqual(user.email, "jane@test.com")

    def test_register_user_email_incorrect(self):
        url = reverse('authentication:register')
        response = self.client.post(
            url,
            data={
                "email": "jane@testcom",
                "password": "!Test1234",
                "re_password": "!Test1234",
                "name": "Jane",
                "surname": "Smith",
                "captcha": "dummy_captcha",
                "company": {
                    "name": "My Company",
                    "is_registered": True,
                    "is_startup": False,
                    "is_fop": False,
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"email": ["Enter a valid email address."]},
            response.json(),
        )

    def test_register_user_email_exists(self):
        url = reverse('authentication:register')
        response = self.client.post(
            url,
            data={
                "email": "test@test.com",
                "password": "Test12!34",
                "re_password": "Test12!34",
                "name": "Test",
                "surname": "Test",
                "captcha": "dummy_captcha",
                "company": {
                    "name": "Test Company",
                    "is_registered": True,
                    "is_startup": False,
                    "is_fop": False,
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"email": ["Email is already registered"]},
            response.json(),
        )

    def test_register_user_password_incorrect(self):
        url = reverse('authentication:register')
        response = self.client.post(
            url,
            data={
                "email": "jane@test.com",
                "password": "te1234",
                "re_password": "tess",
                "name": "Jane",
                "surname": "Smith",
                "captcha": "dummy_captcha",
                "company": {
                    "name": "My Company",
                    "is_registered": True,
                    "is_startup": False,
                    "is_fop": False,
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                "password": [
                    "Password must be at least 8 characters long.",
                    "Password must include at least one uppercase letter (A-Z), one lowercase letter (a-z) and one digit (0-9).",
                    "Password must include at least one special character (e.g., !@#$%^&*).",
                    "Passwords don't match.",
                ]
            },
            response.json(),
        )

    def test_register_user_who_represent_empty_fields(self):
        url = reverse('authentication:register')
        response = self.client.post(
            url,
            data={
                "email": "jane@test.com",
                "password": "Test12!34",
                "re_password": "Test12!34",
                "name": "Jane",
                "surname": "Smith",
                "captcha": "dummy_captcha",
                "company": {
                    "name": "My Company",
                    "is_registered": False,
                    "is_startup": False,
                    "is_fop": False,
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"comp_status": ["Please choose who you represent."]},
            response.json(),
        )

    def test_register_user_who_represent_both_chosen(self):
        url = reverse('authentication:register')
        response = self.client.post(
            url,
            data={
                "email": "jane@test.com",
                "password": "Test12!34",
                "re_password": "Test12!34",
                "name": "Jane",
                "surname": "Smith",
                "captcha": "dummy_captcha",
                "company": {
                    "name": "My Company",
                    "is_registered": True,
                    "is_startup": True,
                    "is_fop": False,
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {
                "name": "Jane",
                "surname": "Smith",
            },
            response.json(),
        )
