"""
Utility functions for the accounts app.

Provides:
    - generate_otp: creates a random 6-digit OTP string
    - store_otp: stores OTP and its expiration in the user's session
    - verify_otp: checks the OTP against the stored value and expiration
    - send_otp_email: sends the OTP via Django's console email backend
    - validate_password_strength: basic password strength validation
"""

import random
import string

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()

# OTP configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5

# Session keys for OTP storage
SESSION_OTP_KEY = 'password_reset_otp'
SESSION_OTP_EMAIL_KEY = 'password_reset_email'
SESSION_OTP_EXPIRY_KEY = 'password_reset_otp_expiry'
SESSION_OTP_USED_KEY = 'password_reset_otp_used'


def generate_otp():
    """Generate a random 6-digit OTP string.

    Returns:
        A string of 6 digits (e.g. '038471').
    """
    digits = string.digits
    return ''.join(random.choices(digits, k=OTP_LENGTH))


def store_otp(request, email, otp):
    """Store the OTP and its expiration time in the user's session.

    Args:
        request: The HTTP request object.
        email: The email address the OTP was sent to.
        otp: The OTP string to store.
    """
    request.session[SESSION_OTP_EMAIL_KEY] = email
    request.session[SESSION_OTP_KEY] = otp
    request.session[SESSION_OTP_EXPIRY_KEY] = (
        timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    ).isoformat()
    request.session[SESSION_OTP_USED_KEY] = False


def get_stored_otp(request):
    """Retrieve the stored OTP data from the session.

    Returns:
        A dict with keys 'otp', 'email', 'expiry', and 'used',
        or None if no OTP is stored.
    """
    otp = request.session.get(SESSION_OTP_KEY)
    if otp is None:
        return None
    return {
        'otp': otp,
        'email': request.session.get(SESSION_OTP_EMAIL_KEY, ''),
        'expiry': request.session.get(SESSION_OTP_EXPIRY_KEY),
        'used': request.session.get(SESSION_OTP_USED_KEY, False),
    }


def is_otp_valid(request, entered_otp):
    """Check whether the entered OTP matches the stored one and is not expired.

    Side effects:
        - Marks the OTP as used if the check passes (one-time use).
        - Clears expired OTP data from the session.

    Args:
        request: The HTTP request object.
        entered_otp: The OTP string entered by the user.

    Returns:
        (is_valid, error_message) tuple.
    """
    data = get_stored_otp(request)
    if data is None:
        return False, 'No OTP request found. Please request a new OTP.'

    # Check if already used
    if data['used']:
        return False, 'This OTP has already been used. Please request a new OTP.'

    # Check expiration
    expiry_str = data['expiry']
    if expiry_str:
        expiry = timezone.datetime.fromisoformat(expiry_str)
        if timezone.now() > expiry:
            clear_otp(request)
            return False, 'The OTP has expired. Please request a new OTP.'

    # Check value
    if data['otp'] != entered_otp:
        return False, 'Incorrect OTP. Please try again.'

    # Mark as used (one-time use)
    request.session[SESSION_OTP_USED_KEY] = True
    return True, None


def clear_otp(request):
    """Remove all OTP-related data from the session."""
    for key in (
        SESSION_OTP_KEY,
        SESSION_OTP_EMAIL_KEY,
        SESSION_OTP_EXPIRY_KEY,
        SESSION_OTP_USED_KEY,
    ):
        request.session.pop(key, None)


def send_otp_email(email, otp):
    """Send the OTP to the given email using Django's console email backend.

    The email content is printed to the server console during development.

    Args:
        email: The recipient email address.
        otp: The OTP string to include in the email.
    """
    subject = 'Your Password Reset OTP'
    message = (
        f'Use the following OTP to reset your password:\n\n'
        f'    {otp}\n\n'
        f'This OTP is valid for {OTP_EXPIRY_MINUTES} minutes.\n'
        f'If you did not request a password reset, please ignore this email.'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_FROM,
        recipient_list=[email],
        fail_silently=False,
    )


def get_user_by_email(email):
    """Look up a user by email address.

    Args:
        email: The email address to search for.

    Returns:
        The User object if found, None otherwise.
    """
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
