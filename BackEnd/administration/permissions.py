import logging
from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS
)


logger = logging.getLogger(__name__)


class IsStaffUser(BasePermission):
    """
    Custom is staff permission.
    """

    def has_permission(self, request, view):
        return request.user.is_staff


class IsStaffUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class HasRolePermission(BasePermission):
    """
    Custom permission to check if the user has a specific role.
    """
    def __init__(self, role_name):
        self.role_name = role_name

    def has_permission(self, request, view):
        has_role = request.user.roles.filter(name=self.role_name).exists()
        log_level = logger.info if has_role else logger.warning
        log_level(
            f"User {request.user.email} {'has' if has_role else 'does not have'} required role '{self.role_name}' for {request.method} {request.path}")
        return has_role


class IsAdminUser(HasRolePermission):
    """
    Custom permission to check if the user has the 'Admin' role.
    """
    def __init__(self):
        super().__init__("Admin")


class IsModeratorUser(HasRolePermission):
    """
    Custom permission to check if the user has the 'Moderator' role.
    """
    def __init__(self):
        super().__init__("Moderator")
