from rest_framework import status
from rest_framework.test import APITestCase

from custom_auth.factories import UserFactory


class UserLogoutAPITests(APITestCase):
    def setUp(self):
        self.user = UserFactory(email="test@test.com")

    def test_logout_successful(self):
        self.user.set_password("Test1234")
        self.user.save()
        login_response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
            },
        )
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        # Logout with refresh token
        response = self.client.post(
            path="/api/auth/logout/",
            data={"refresh": refresh_token},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": "Logged out successfully."},
            response.json(),
        )

    def test_logout_not_logged_in(self):
        response = self.client.post(
            path="/api/auth/logout/",
            data={"refresh": "invalid_token"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {'detail': 'Authentication credentials were not provided.'},
            response.json(),
        )

    def test_logout_with_invalid_token(self):
        response = self.client.post(
            path="/api/auth/logout/",
            data={"refresh": "invalid_token"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {'detail': 'Authentication credentials were not provided.'},
            response.json(),
        )

    def test_logout_with_reused_token(self):
        self.user.set_password("Test1234")
        self.user.save()
        login_response = self.client.post(
            path="/api/auth/login/",
            data={"email": "test@test.com", "password": "Test1234"},
        )
        refresh_token = login_response.data["refresh"]
        self.client.post(
            path="/api/auth/logout/",
            data={"refresh": refresh_token},
        )
        response = self.client.post(
            path="/api/auth/logout/",
            data={"refresh": refresh_token},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
