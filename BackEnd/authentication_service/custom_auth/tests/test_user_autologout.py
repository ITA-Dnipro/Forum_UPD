from datetime import timedelta
from django.utils.timezone import now

from unittest.mock import patch

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from custom_auth.factories import UserFactory
from profiles.factories import ProfileCompanyFactory
from utils.unittest_helper import AnyInt


class UserLogoutAPITests(APITestCase):
    def setUp(self):
        patcher = patch(
            "authentication.serializers.verify_recaptcha", return_value=True
        )
        self.mock_verify_recaptcha = patcher.start()
        self.addCleanup(patcher.stop)

        self.user = UserFactory(
            email="test@test.com", name="Test", surname="Test"
        )
        self.profile = ProfileCompanyFactory.create(
            person=self.user,
            official_name="Test Official Startup",
        )

    def test_user_autologout_after_14_days(self):
        self.user.set_password("Test1234")
        self.user.save()

        response = self.client.post(
            path="/api/auth/token/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
                "captcha": "dummy_captcha",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login failed")
        self.assertIn("auth_token", response.data, "auth_token missing in response")

        self.test_user_token = response.data["auth_token"]

        Token.objects.filter(key=self.test_user_token).update(created=now()  - timedelta(days=15))

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.test_user_token}"
        )

        response = self.client.get(path="/api/auth/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Your session has expired. Please login again."},
            response.json(),
        )

    def test_user_autologout_after_10_days(self):
        self.user.set_password("Test1234")
        self.user.save()

        self.test_user_token = self.client.post(
            path="/api/auth/token/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
                "captcha": "dummy_captcha",
            },
        ).data["auth_token"]

        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login failed")
        self.assertIn("auth_token", response.data, "auth_token missing in response")

        self.test_user_token = response.data["auth_token"]

        Token.objects.filter(key=self.test_user_token).update(created=now() - timedelta(days=10))
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.test_user_token}"
        )
        response = self.client.get(path="/api/auth/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {
                "id": AnyInt(),
                "email": "test@test.com",
                "name": "Test",
                "surname": "Test",
                "profile_id": AnyInt(),
                "is_staff": False,
                "is_superuser": False,
            },
            response.json(),
        )
