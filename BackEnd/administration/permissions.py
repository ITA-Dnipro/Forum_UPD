from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS
)


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
    Grants access if a user has any of the specified roles.
    Example usage: HasAnyRolePermission(["Admin", "Moderator"])
    """
    allowed_roles = []

    def has_permission(self, request, view):
        """
        Checks if the user has the required role.
        Returns True if the user has the role, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.roles.filter(name__in=self.allowed_roles).exists()


class IsAdminUser(HasRolePermission):
    """
    Custom permission to check if the user has the 'Admin' role.
    """
    role_name = "Admin"


class IsModeratorUser(HasRolePermission):
    """
    Custom permission to check if the user has the 'Moderator' role.
    """
    role_name = "Moderator"
