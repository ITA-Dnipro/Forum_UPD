from rest_framework import status
from rest_framework.test import APITestCase
from custom_auth.models import Role
from custom_auth.factories import UserFactory


class UserLoginAPITests(APITestCase):
    def setUp(self):
        self.user = UserFactory(email="test@test.com")

    def test_login_successful_investor(self):
        self.user.set_password("Test1234")
        investor_role = Role.objects.get(name="Investor")
        self.user.roles.add(investor_role)
        self.user.save()
        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
                "login_option": "Investor",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_login_successful_startup(self):
        self.user.set_password("Test1234")
        investor_role = Role.objects.get(name="Startup")
        self.user.roles.add(investor_role)
        self.user.save()
        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
                "login_option": "Startup",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_login_incorrect_startup(self):
        self.user.set_password("Test1234")
        self.user.save()
        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
                "login_option": "Startup",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not registered as a startup", response.data)

    def test_login_incorrect_investor(self):
        self.user.set_password("Test1234")
        self.user.save()
        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
                "login_option": "Investor",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not registered as an investor", response.data)

    def test_login_email_incorrect(self):
        self.user.set_password("Test1234")
        investor_role = Role.objects.get(name="Investor")
        self.user.roles.add(investor_role)
        self.user.save()

        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "tost@test.com",
                "password": "Test1234",
                "login_option": "Investor",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Invalid password or email",
            response.data.values(),
        )

    def test_login_password_incorrect(self):
        self.user.set_password("Test1234")
        self.user.save()

        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test5678",
                "login_option": "Investor",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Invalid password or email",
            response.data.values(),
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
                    "login_option": "Investor",
                },
            )
        response = self.client.post(
            path="/api/auth/login/",
            data={
                "email": "test@test.com",
                "password": "Test1234",
                "login_option": "Investor",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
