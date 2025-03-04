from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from custom_auth.factories import UserFactory
from custom_auth.models import CustomUser

url = reverse('authentication:register')


class UserRegistrationAPITests(APITestCase):
    def setUp(self):
        patcher = patch(
            "authentication.serializers.verify_recaptcha", return_value=True
        )
        self.mock_verify_recaptcha = patcher.start()
        self.addCleanup(patcher.stop)

        self.existing_user = UserFactory.create(email="test@test.com")

        self.default_payload = {
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
        }

    def test_register_user_email_incorrect(self):
        payload = self.default_payload.copy()
        payload["email"] = "jane@testcom"

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"email": ["Enter a valid email address."]}, response.json())

    def test_register_user_email_exists(self):
        payload = self.default_payload.copy()
        payload["email"] = self.existing_user.email

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"email": ["Email is already registered"]}, response.json())

    def test_register_user_password_incorrect(self):
        payload = self.default_payload.copy()
        test_user = UserFactory.build()
        payload["email"] = test_user.email
        payload["password"] = "te1234"
        payload["re_password"] = "tess"

        response = self.client.post(url, data=payload, format="json")
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
        test_user = UserFactory.build()
        payload = self.default_payload.copy()
        payload["email"] = test_user.email
        payload["company"] = {
            "name": "My Company Empty",
            "is_registered": False,
            "is_startup": False,
            "is_fop": False,
        }

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"comp_status": ["Please choose who you represent."]}, response.json())

    def test_register_user_both_companies_chosen(self):
        test_user = UserFactory.build()
        payload = self.default_payload.copy()
        payload["email"] = test_user.email
        payload["company"] = {
            "name": "My Company Startup FOP",
            "is_registered": True,
            "is_startup": True,
            "is_fop": True,
        }

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({"name": "Jane", "surname": "Smith"}, response.json())

    def test_register_user_yurosoba_successful(self):
        test_user = UserFactory.build()
        payload = self.default_payload.copy()
        payload["email"] = test_user.email
        payload["company"] = {
            "name": "My Company yurosoba",
            "is_registered": True,
            "is_startup": False,
            "is_fop": False,
        }

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({"name": "Jane", "surname": "Smith"}, response.json())

    def test_register_user_fop_successful(self):
        test_user = UserFactory.build()
        payload = self.default_payload.copy()
        payload["email"] = test_user.email
        payload["company"] = {
            "name": "My Company FOP",
            "is_registered": True,
            "is_startup": False,
            "is_fop": True,
        }

        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({"name": "Jane", "surname": "Smith"}, response.json())
