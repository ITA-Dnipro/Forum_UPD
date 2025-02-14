from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factories import UserFactory
from utils.dump_response import dump  # noqa


class UserLoginAPITests(APITestCase):
    def setUp(self):
        self.user = UserFactory(email="test@test.com")

    def test_login_successful(self):
        self.user.set_password("Test1234")
        self.user.save()
        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_login_email_incorrect(self):
        self.user.set_password("Test1234")
        self.user.save()

        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "tost@test.com",
                "password": "Test1234",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "No active account found with the given credentials"},
            response.json(),
        )

    def test_login_password_incorrect(self):
        self.user.set_password("Test1234")
        self.user.save()

        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test5678",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "No active account found with the given credentials"},
            response.json(),
        )

    def test_login_after_allowed_delay_time(self):
        self.user.set_password("Test1234")
        self.user.save()

        for _ in range(3):
            self.client.post(
                path="/api/auth/login/",
                data={
                    "email": "test@test.com",
                    "password": "wrong_password",
                },
            )
        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
