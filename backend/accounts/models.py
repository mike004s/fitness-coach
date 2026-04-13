from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended user model for KINETIC.
    Uses email as the primary identifier while keeping username for
    Django admin compatibility.
    """
    email = models.EmailField(unique=True)

    # Optional profile fields
    full_name = models.CharField(max_length=150, blank=True)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_display_name(self):
        return self.full_name or self.email.split('@')[0]
