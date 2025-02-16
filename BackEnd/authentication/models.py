from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    roles = models.ManyToManyField("Role", related_name="users", blank=True)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = [
        "surname",
        "name",
    ]

    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

    def has_permission(self, perm, obj=None):
        """
        Checks if the user has a specific permission.

        Args:
            perm (str): The permission codename to check.
            obj (optional): The object to check the permission against. Defaults to None.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        if self.is_superuser:
            return True
        return self.roles.filter(permissions__codename=perm).exists()


class Permission(models.Model):
    """
    Model for storing permissions in the system.
    Each permission has a name and a unique codename.

    Fields:
        name (CharField): The human-readable name of the permission.
        codename (CharField): The unique codename of the permission.
    """
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Model for storing roles in the system.
    Each role has a name and can be associated with multiple permissions.

    Fields:
        name (CharField): The name of the role.
        permissions (ManyToManyField): The permissions associated with the role.
    """
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        related_name="roles",
        blank=True
    )

    def __str__(self):
        return self.name
