"""
Views for the accounts app.

All authentication-related views are implemented here:
    - Registration (distributor only)
    - Admin login / dashboard / logout
    - Distributor login / dashboard / logout
    - Password recovery (forgot password, verify OTP, reset password)

Role-based access control is enforced via custom decorators
(see ``accounts.decorators``).
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .decorators import admin_required, distributor_required
from .forms import (
    AdminLoginForm,
    DistributorLoginForm,
    DistributorRegistrationForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    VerifyOTPForm,
)
from .utils import (
    clear_otp,
    generate_otp,
    get_user_by_email,
    is_otp_valid,
    send_otp_email,
    store_otp,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

def home_view(request):
    """Home page with links to login and registration."""
    return render(request, 'authentication/home.html')


# ---------------------------------------------------------------------------
# Registration (distributor only)
# ---------------------------------------------------------------------------

def register_view(request):
    """Distributor registration page.

    Only DISTRIBUTOR users can register from the frontend. Admin
    users are created via the Django admin panel or createsuperuser.

    On successful registration, the user is redirected to the
    distributor login page with a success message.
    """
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('accounts:admin_dashboard')
        return redirect('accounts:distributor_dashboard')

    if request.method == 'POST':
        form = DistributorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Account created for {user.username}. You can now log in.',
            )
            return redirect('accounts:distributor_login')
    else:
        form = DistributorRegistrationForm()

    return render(request, 'authentication/register.html', {'form': form})


# ---------------------------------------------------------------------------
# Admin login / dashboard / logout
# ---------------------------------------------------------------------------

def admin_login_view(request):
    """Admin login page.

    Only users with the ADMIN role can log in here. If a distributor
    tries to log in, an "unauthorized" message is shown.
    """
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('accounts:admin_dashboard')
        return redirect('accounts:distributor_dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                if user.is_admin:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}.')
                    return redirect('accounts:admin_dashboard')
                else:
                    messages.error(request, 'You are not authorized.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AdminLoginForm()

    return render(request, 'authentication/admin_login.html', {'form': form})


@admin_required
def admin_dashboard_view(request):
    """Admin dashboard showing welcome message and user info."""
    return render(request, 'authentication/admin_dashboard.html', {
        'user': request.user,
    })


@admin_required
def admin_logout_view(request):
    """Logout for admin users."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:admin_login')


# ---------------------------------------------------------------------------
# Distributor login / dashboard / logout
# ---------------------------------------------------------------------------

def distributor_login_view(request):
    """Distributor login page.

    Only users with the DISTRIBUTOR role can log in here. If an admin
    tries to log in, an "unauthorized" message is shown.
    """
    if request.user.is_authenticated:
        if request.user.is_distributor:
            return redirect('accounts:distributor_dashboard')
        return redirect('accounts:admin_dashboard')

    if request.method == 'POST':
        form = DistributorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                if user.is_distributor:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}.')
                    return redirect('accounts:distributor_dashboard')
                else:
                    messages.error(request, 'You are not authorized.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = DistributorLoginForm()

    return render(request, 'authentication/distributor_login.html', {'form': form})


@distributor_required
def distributor_dashboard_view(request):
    """Distributor dashboard showing welcome message and user info."""
    return render(request, 'authentication/distributor_dashboard.html', {
        'user': request.user,
    })


@distributor_required
def distributor_logout_view(request):
    """Logout for distributor users."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:distributor_login')


# ---------------------------------------------------------------------------
# Password Recovery (OTP)
# ---------------------------------------------------------------------------

def forgot_password_view(request):
    """Forgot password page — user enters email to receive OTP.

    Generates a 6-digit OTP, stores it in the session with a 5-minute
    expiry, and sends it via the console email backend.
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_by_email(email)
            if user is None:
                messages.error(
                    request,
                    'No account found with this email address.',
                )
                return redirect('accounts:forgot_password')

            otp = generate_otp()
            store_otp(request, email, otp)
            send_otp_email(email, otp)
            messages.success(
                request,
                'An OTP has been sent to your email. Please check the server console.',
            )
            return redirect('accounts:verify_otp')
    else:
        form = ForgotPasswordForm()

    return render(request, 'authentication/forgot_password.html', {'form': form})


def verify_otp_view(request):
    """OTP verification page.

    Validates the entered OTP against the stored value. If correct,
    the user is redirected to the reset password page. The OTP is
    one-time use and expires after 5 minutes.
    """
    # Guard: no OTP was requested
    from .utils import get_stored_otp
    if get_stored_otp(request) is None:
        messages.error(request, 'Please request an OTP first.')
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            is_valid, error_msg = is_otp_valid(request, entered_otp)
            if is_valid:
                messages.success(request, 'OTP verified. Please set a new password.')
                return redirect('accounts:reset_password')
            else:
                messages.error(request, error_msg)
    else:
        form = VerifyOTPForm()

    return render(request, 'authentication/verify_otp.html', {'form': form})


def reset_password_view(request):
    """Reset password page — user sets a new password after OTP verification.

    Requires that the OTP was successfully verified (checked via the
    session flag). The new password is validated for strength and
    the confirm password must match.
    """
    from .utils import get_stored_otp

    # Guard: OTP must have been verified
    data = get_stored_otp(request)
    if data is None or not data['used']:
        messages.error(request, 'Please verify your OTP first.')
        return redirect('accounts:forgot_password')

    email = data.get('email', '')
    user = get_user_by_email(email)
    if user is None:
        messages.error(request, 'Account not found. Please try again.')
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            clear_otp(request)
            messages.success(
                request,
                'Password reset successfully. You can now log in.',
            )
            # Redirect to the appropriate login page based on role
            if user.is_admin:
                return redirect('accounts:admin_login')
            return redirect('accounts:distributor_login')
    else:
        form = ResetPasswordForm()

    return render(request, 'authentication/reset_password.html', {'form': form})
