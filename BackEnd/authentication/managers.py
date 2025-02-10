from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Creates and returns a regular user.
        
        :param email (str): The email address of the user.
        :param password (str): The user's password.
        :param **extra_fields: Additional user fields.

        Returns:
            CustomUser: The created user instance.
        """

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and returns a superuser with elevated permissions.
        
        :param email (str): The email address of the superuser.
        :param password (str): The superuser's password.
        :param **extra_fields: Additional superuser fields.

        Returns:
            CustomUser: The created superuser instance.
        """

        user = self.create_user(email, password=password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user