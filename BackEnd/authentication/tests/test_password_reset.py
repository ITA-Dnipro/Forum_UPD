from django.core.signing import TimestampSigner
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factories import UserFactory

signer = TimestampSigner()


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = UserFactory(
            email="test@example.com"
        )
        self.user.set_password("OldPassword123")
        self.user.save()

    def test_password_reset_request(self):
        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": self.user.email},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Mail outbox:", mail.outbox)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password Reset Request", mail.outbox[0].subject)
        self.assertIn("The link for password reset was sent. Please, check you mail.", response.data["message"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm(self):
        token = signer.sign(self.user.pk)
        response = self.client.post(
            "/api/auth/password-reset-confirm/",
            {"token": token, "new_password": "NewSecurePass123!"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], "The password was updated successfully."
        )

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
