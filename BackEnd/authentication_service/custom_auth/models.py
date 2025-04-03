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
    roles = models.ManyToManyField("Role", through="UserRole", related_name="users", blank=True)

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
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    UserRole model links users with roles and tracks their validation status.
    Each user can have at most one 'startup' role and one 'investor' role.
    """
    NOT_VALIDATED = "not_validated"
    VALIDATED = "validated"

    STATUS_CHOICES = [
        (NOT_VALIDATED, "Not Validated"),
        (VALIDATED, "Validated"),
    ]

    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey("Role", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NOT_VALIDATED)

    class Meta:
        unique_together = ("user", "role")  # Prevents having the same user with the same role twice

    def __str__(self):
        return f"{self.user.email} - {self.role.name} ({self.status})"
