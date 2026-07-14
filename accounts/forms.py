"""
Forms for the accounts app.

Provides:
    - DistributorRegistrationForm: registration form for distributor users
    - AdminLoginForm: login form for admin users
    - DistributorLoginForm: login form for distributor users
    - ForgotPasswordForm: email input for OTP request
    - VerifyOTPForm: 6-digit OTP input
    - ResetPasswordForm: new password + confirm password

All forms use Bootstrap 5 styling via the ``__init__`` method that
adds the ``form-control`` CSS class to all fields.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class BootstrapFormMixin:
    """Mixin that adds Bootstrap 5 ``form-control`` class to all fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] += ' form-control'


class DistributorRegistrationForm(BootstrapFormMixin, UserCreationForm):
    """Registration form for distributor users only.

    Fields:
        - First Name, Last Name, Email, Username, Phone Number,
          Password, Confirm Password.

    Validation:
        - Username must be unique.
        - Email must be unique.
        - Password and confirm password must match (inherited from
          UserCreationForm).
        - Password strength is validated via Django's password
          validators (configured in settings).
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+1 234 567 890'}),
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'phone_number',
        )

    def clean_email(self):
        """Ensure the email address is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        """Ensure the username is unique (case-insensitive)."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        """Save the new user with the DISTRIBUTOR role."""
        user = super().save(commit=False)
        user.role = User.Role.DISTRIBUTOR
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class AdminLoginForm(BootstrapFormMixin, forms.Form):
    """Login form for admin users."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )


class DistributorLoginForm(BootstrapFormMixin, forms.Form):
    """Login form for distributor users."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )


class ForgotPasswordForm(BootstrapFormMixin, forms.Form):
    """Email input form for password recovery."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )


class VerifyOTPForm(BootstrapFormMixin, forms.Form):
    """6-digit OTP verification form."""

    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit OTP',
            'pattern': '[0-9]{6}',
            'title': 'Enter the 6-digit code',
        }),
    )

    def clean_otp(self):
        """Ensure the OTP contains only digits."""
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise ValidationError('OTP must contain only digits.')
        return otp


class ResetPasswordForm(BootstrapFormMixin, forms.Form):
    """New password and confirm password form for password reset."""

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password'}),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
    )

    def clean_new_password(self):
        """Validate password strength using Django's validators."""
        password = self.cleaned_data.get('new_password')
        from django.contrib.auth.password_validation import validate_password
        validate_password(password)
        return password

    def clean(self):
        """Ensure new password and confirm password match."""
        cleaned = super().clean()
        new_pw = cleaned.get('new_password')
        confirm_pw = cleaned.get('confirm_password')
        if new_pw and confirm_pw and new_pw != confirm_pw:
            raise ValidationError('Passwords do not match.')
        return cleaned
