"""
App configuration for the accounts app.

Overrides ``ready()`` to import signal handlers so that post-save
signals are connected when the app starts.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User Accounts'

    def ready(self):
        """Import signals when the app is ready."""
        from . import signals  # noqa: F401
