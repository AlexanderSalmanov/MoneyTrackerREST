from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, full_name=None, password=None, **extra_fields):

        if not email:
            raise ValueError("Users must have an email!")
        if not password:
            raise ValueError("Users must have a password!")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            full_name=full_name,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, full_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superusers should have is_staff = True")
        if not extra_fields.get('is_admin'):
            raise ValueError("Superusers should have is_admin = True")

        user = self.create_user(
            email=email,
            full_name=full_name,
            password=password,
            **extra_fields
        )

        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=128, unique=True, db_index=True)
    full_name = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def tokens(self):
        tokens = RefreshToken.for_user(self)
        return {
            'access': str(tokens.access_token),
            'refresh': str(tokens) # defaults to refresh!
        }

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        if self.full_name:
            if len(self.full_name.split(' ')) > 1:
                return self.full_name.split(' ')[0]
            return self.full_name
        return self.email

    @property
    def is_superuser(self):
        return self.is_admin
