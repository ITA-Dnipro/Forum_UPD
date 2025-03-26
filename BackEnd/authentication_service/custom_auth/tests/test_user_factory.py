from django.test import TestCase

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from custom_auth.factories import UserFactory


class TestFactories(TestCase):
    def test_user_factory(self):
        user = UserFactory()
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.name)
        self.assertIsNotNone(user.surname)
        self.assertTrue(user.is_active)

        try:
            validate_email(user.email)
        except ValidationError:
            self.fail(f"Invalid email generated: {user.email}")
