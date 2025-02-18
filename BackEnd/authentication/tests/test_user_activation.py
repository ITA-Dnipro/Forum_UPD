from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.signing import(
    TimestampSigner,
    BadSignature,
)

from datetime import timedelta
from authentication.factories import UserFactory
from utils.dump_response import dump  # noqa


url = reverse('authentication:activate')

class AccountActivationAPITests(APITestCase):
    def setUp(self):
        patcher = patch(
            "authentication.serializers.verify_recaptcha", return_value=True
        )
        self.mock_verify_recaptcha = patcher.start()
        self.addCleanup(patcher.stop)
        self.test_user = UserFactory.create(is_active=False)

        self.signer = TimestampSigner()

    def test_account_activation_success(self):
        token = self.signer.sign(str(self.test_user.pk))
        response = self.client.get(f"{url}?token={token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_user.refresh_from_db()

        self.assertTrue(self.test_user.is_active)
        self.assertEqual(response.json(), {"detail": "Account activated successfully."})

    def test_account_activation_missing_token(self):
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "No token provided."})

    def test_account_activation_invalid_token(self):
        invalid_token = "invalid_token"
        response = self.client.get(f"{url}?token={invalid_token}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid or expired token."})

    def test_account_activation_user_not_found(self):
        invalid_token = self.signer.sign("999")
        response = self.client.get(f"{url}?token={invalid_token}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "User not found."})

    def test_account_activation_expired_token(self):
        token = self.signer.sign(str(self.test_user.pk))

        expired_token = self.signer.sign(str(self.test_user.pk))
        expired_time = timezone.now() - timedelta(hours=2)

        with patch('django.core.signing.TimestampSigner.unsign') as mock_unsign:
            mock_unsign.side_effect = BadSignature

            response = self.client.get(f"{url}?token={expired_token}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid or expired token."})
