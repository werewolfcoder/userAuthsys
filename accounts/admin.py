"""
Admin panel registration for the accounts app.

Registers the custom User model with Django's admin site, displaying
username, email, role, active status, and date joined. This allows
admins to manage users directly from the Django admin panel.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model.

    Displays username, email, role, active status, and date joined
    in the list view. The role and phone number fields are included
    in the edit form so admins can manage user roles.
    """

    list_display = (
        'username',
        'email',
        'role',
        'is_active',
        'date_joined',
    )
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number'),
        }),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )
