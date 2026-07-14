"""
Signals for the accounts app.

Post-save signal handler that ensures every new user gets a default
role of DISTRIBUTOR unless explicitly set otherwise (e.g. via the
admin panel or createsuperuser).
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def set_default_role(sender, instance, created, **kwargs):
    """Ensure new users have a role assigned.

    Superusers created via ``createsuperuser`` are automatically
    assigned the ADMIN role if no role has been set.
    """
    if created and instance.is_superuser and instance.role != User.Role.ADMIN:
        instance.role = User.Role.ADMIN
        instance.save(update_fields=['role'])
