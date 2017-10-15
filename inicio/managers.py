from  django.contrib.auth import hashers
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self,email, password, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        if not email:
            raise ValueError('The given username must be set')
        email = email

        user = self.model( email=email, **extra_fields)
        print(password)
        user.set_password(password)
        user.is_staff=True
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
