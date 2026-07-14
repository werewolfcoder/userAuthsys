"""
Custom decorators for role-based access control.

Provides:
    - role_login_required: ensures the user is authenticated
    - admin_required: ensures the user is authenticated AND is an Admin
    - distributor_required: ensures the user is authenticated AND is a Distributor

Unauthorized users are redirected to the appropriate login page with
an error message via the Django messages framework.
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_login_required(redirect_name):
    """Decorator factory that checks authentication.

    If the user is not authenticated, they are redirected to the
    given URL name with an error message.

    Args:
        redirect_name: The URL pattern name to redirect to on failure.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect(redirect_name)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def admin_required(view_func):
    """Restrict access to authenticated Admin users only.

    Redirects unauthenticated users to the admin login page.
    Authenticated non-admin users receive an "unauthorized" message.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('accounts:admin_login')
        if not request.user.is_admin:
            messages.error(request, 'You are not authorized.')
            return redirect('accounts:admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped


def distributor_required(view_func):
    """Restrict access to authenticated Distributor users only.

    Redirects unauthenticated users to the distributor login page.
    Authenticated non-distributor users receive an "unauthorized" message.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('accounts:distributor_login')
        if not request.user.is_distributor:
            messages.error(request, 'You are not authorized.')
            return redirect('accounts:distributor_login')
        return view_func(request, *args, **kwargs)
    return _wrapped
