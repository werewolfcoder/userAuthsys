"""
URL configuration for the accounts app.

All authentication-related routes are defined here:
    - Home page
    - Registration (distributor only)
    - Admin login / dashboard
    - Distributor login / dashboard
    - Password recovery (forgot password, verify OTP, reset password)
    - Logout
"""

from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),

    # Registration (distributor only)
    path('register/', views.register_view, name='register'),

    # Admin login / dashboard / logout
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout_view, name='admin_logout'),

    # Distributor login / dashboard / logout
    path('distributor-login/', views.distributor_login_view, name='distributor_login'),
    path('distributor-dashboard/', views.distributor_dashboard_view, name='distributor_dashboard'),
    path('distributor-logout/', views.distributor_logout_view, name='distributor_logout'),

    # Password recovery
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
]
