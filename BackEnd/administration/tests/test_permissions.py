from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import CustomUser, Permission, Role
from administration.models import AutoModeration
from administration.urls import app_name


class RBACPermissionTests(APITestCase):
    """
    Test suite for Role-Based Access Control (RBAC) functionality.
    This suite verifies that users with different roles (Admin, Moderator, Regular)
    have appropriate access to protected API endpoints.
    """
    def setUp(self):
        self.view_permission = Permission.objects.create(
            name="View Permission", codename="view_permission"
        )
        self.edit_permission = Permission.objects.create(
            name="Edit Permission", codename="edit_permission"
        )

        self.admin_role = Role.objects.create(name="Admin")
        self.moderator_role = Role.objects.create(name="Moderator")

        self.admin_role.permissions.add(self.view_permission, self.edit_permission)
        self.moderator_role.permissions.add(self.view_permission)

        self.admin_user = CustomUser.objects.create(email="admin@test.com", is_active=True)
        self.admin_user.roles.add(self.admin_role)

        self.moderator_user = CustomUser.objects.create(email="moderator@test.com", is_active=True)
        self.moderator_user.roles.add(self.moderator_role)

        self.regular_user = CustomUser.objects.create(email="user@test.com", is_active=True)

        self.auto_moderation, _ = AutoModeration.objects.get_or_create(auto_moderation_hours=12)

    def tearDown(self):
        """
        Clean up test data after each test:
        - Delete all AutoModeration objects
        - Delete all CustomUser objects
        - Delete all Role objects
        - Delete all Permission objects
        """
        AutoModeration.objects.all().delete()
        CustomUser.objects.all().delete()
        Role.objects.all().delete()
        Permission.objects.all().delete()

    def test_admin_access_to_protected_endpoints(self):
        """
        Verify that Admin user has access to all protected endpoints:
        - Can view users list
        - Can view profiles list
        - Can modify auto moderation settings
        """
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(reverse(f'{app_name}:users-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse(f'{app_name}:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            reverse(f'{app_name}:automoderation_hours'),
            {'auto_moderation_hours': 24},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moderator_access_to_protected_endpoints(self):
        """
        Verify that Moderator user has limited access:
        - Can view profiles list
        - Cannot access admin-only endpoints (users list)
        - Cannot modify auto moderation settings
        """
        self.client.force_authenticate(user=self.moderator_user)

        response = self.client.get(reverse(f'{app_name}:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse(f'{app_name}:users-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse(f'{app_name}:automoderation_hours'),
            {'auto_moderation_hours': 24},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_access_to_protected_endpoints(self):
        """
        Verify that Regular user has no access to protected endpoints:
        - Cannot access admin endpoints (users list)
        - Cannot access moderator endpoints (profiles list)
        - Cannot modify auto moderation settings
        """
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(reverse(f'{app_name}:users-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(reverse(f'{app_name}:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse(f'{app_name}:automoderation_hours'),
            {'auto_moderation_hours': 24},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_to_protected_endpoints(self):
        """
        Verify that unauthenticated users receive 401 Unauthorized when accessing protected endpoints.
        """
        response = self.client.get(reverse(f'{app_name}:users-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(reverse(f'{app_name}:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(
            reverse(f'{app_name}:automoderation_hours'),
            {'auto_moderation_hours': 24},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_without_role_access(self):
        """
        Verify that users without a role cannot access any protected endpoints.
        """
        user_without_role = CustomUser.objects.create(email="nobody@test.com", is_active=True)
        self.client.force_authenticate(user=user_without_role)

        response = self.client.get(reverse(f'{app_name}:users-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(reverse(f'{app_name}:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_multiple_roles(self):
        """
        Verify that a user with multiple roles (Admin + Moderator) gets the highest level of access.
        """
        multi_role_user = CustomUser.objects.create(email="multi@test.com", is_active=True)
        multi_role_user.roles.add(self.admin_role, self.moderator_role)
        self.client.force_authenticate(user=multi_role_user)

        response = self.client.get(reverse(f'{app_name}:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Admin-level access

        response = self.client.get(reverse(f'{app_name}:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Moderator-level access

        response = self.client.patch(
            reverse(f'{app_name}:automoderation-detail'),
            {'auto_moderation_hours': 24},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Admin-level access
