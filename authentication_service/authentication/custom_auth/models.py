from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser):
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


class Role(models.Model):
    """
    Model for storing roles in the system.
    Each role has a name and can be associated with multiple permissions.

    Fields:
        name (CharField): The name of the role.
        permissions (ManyToManyField): The permissions associated with the role.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
