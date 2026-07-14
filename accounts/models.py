"""
Models for the accounts app.

This module defines the custom User model that extends Django's
AbstractUser and adds a ``role`` field with two choices: ADMIN and
DISTRIBUTOR.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access.

    Extends Django's AbstractUser to add a ``role`` field that
    distinguishes between Admin and Distributor users. All
    authentication and password handling is inherited from
    AbstractUser, so passwords are hashed automatically.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DISTRIBUTOR = 'DISTRIBUTOR', 'Distributor'

    # Additional fields
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DISTRIBUTOR,
        help_text='Designates whether this user is an Admin or Distributor.',
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        default='',
        help_text='Phone number of the user (distributors).',
    )

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        """Return True if the user has the ADMIN role."""
        return self.role == self.Role.ADMIN

    @property
    def is_distributor(self):
        """Return True if the user has the DISTRIBUTOR role."""
        return self.role == self.Role.DISTRIBUTOR
