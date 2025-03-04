from django.core.cache import cache
from django.core.signing import TimestampSigner
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from custom_auth.factories import UserFactory

signer = TimestampSigner()


class PasswordResetTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.user = UserFactory(
            email="test@example.com"
        )
        self.user.set_password("OldPassword123")
        self.user.save()
        mail.outbox = []

    def test_password_reset_request_existing_email(self):
        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": self.user.email},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Mail outbox:", mail.outbox)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password Reset Request", mail.outbox[0].subject)
        self.assertIn("If an account with that email exists", response.data["message"])

    def test_password_reset_request_nonexistent_email(self):
        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": "nonexistent@example.com"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("If an account with that email exists", response.data["message"])

    def test_password_reset_request_rate_limiting(self):
        response1 = self.client.post(
            "/api/auth/password-reset/",
            {"email": self.user.email},
            format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        response2 = self.client.post(
            "/api/auth/password-reset/",
            {"email": self.user.email},
            format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_password_reset_confirm_valid(self):
        token = signer.sign(f"{self.user.pk}:{self.user.password}")
        response = self.client.post(
            "/api/auth/password-reset-confirm/",
            {"token": token, "new_password": "NewSecurePass123!"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "The password was updated successfully.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePass123!"))

    def test_password_reset_confirm_invalid_token(self):
        response = self.client.post(
            "/api/auth/password-reset-confirm/",
            {"token": "invalidtoken", "new_password": "NewSecurePass123!"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token is invalid or expired.", response.data["error"])

    def test_password_reset_confirm_weak_password(self):
        token = signer.sign(f"{self.user.pk}:{self.user.password}")
        response = self.client.post(
            "/api/auth/password-reset-confirm/",
            {"token": token, "new_password": "123"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("security requirements", response.data.get("error", "").lower())

    def test_password_change_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/auth/password-change/",
            {"old_password": "OldPassword123",
             "new_password": "NewSecurePass123!",
             "confirm_password": "NewSecurePass123!"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Password was updated successfully."
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePass123!"))
