# User Authentication Setup

A Django authentication project with two user roles — **Admin** and **Distributor** — featuring separate login pages, separate dashboards, distributor registration, and OTP-based password recovery.

## Tech Stack

- **Backend:** Python 3.13, Django 5.1
- **Database:** SQLite
- **Frontend:** HTML, Bootstrap 5, Django Template Engine
- **Authentication:** Django Authentication Framework with a Custom User Model

## Project Overview

This project implements a role-based authentication system:

- **Admin** users can log in via `/admin-login/` and access `/admin-dashboard/`. Admins are created via the Django admin panel or `createsuperuser` — they cannot register from the frontend.
- **Distributor** users can register at `/register/`, log in via `/distributor-login/`, and access `/distributor-dashboard/`.
- Password recovery uses a 6-digit OTP sent via SMTP email. The OTP expires after 5 minutes and is one-time use.

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd user-authentication-setup
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

**Linux / macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Copy the example file and edit if needed:

```bash
cp .env.example .env
```

### 6. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser (Admin account)

```bash
python manage.py createsuperuser
```

After creating the superuser, log in to the Django admin panel at `/admin/` and set the user's role to **ADMIN** if needed.

### 8. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## OTP Testing

The project uses an SMTP email backend to send OTP emails to the user's inbox.

### Email Setup

1. Configure your SMTP credentials in the `.env` file (copy from `.env.example`):

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

2. For Gmail, generate an **App Password** at https://myaccount.google.com/apppasswords (regular passwords won't work).

3. Restart the server after updating `.env`.

### OTP Flow

1. Go to `/forgot-password/`.
2. Enter a registered email address.
3. Check the email inbox for the OTP message.
4. Enter the 6-digit OTP on the verify page.
5. If the OTP is correct and not expired (5 minutes), you will be redirected to set a new password.

## Folder Structure

```
user-authentication-setup/
├── accounts/                  # Main authentication app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                # Admin panel registration
│   ├── apps.py
│   ├── decorators.py            # Custom role-based decorators
│   ├── forms.py                 # Registration, login, OTP forms
│   ├── models.py                # Custom User model
│   ├── signals.py               # Post-save signals (if needed)
│   ├── urls.py                  # App-level URL routes
│   ├── utils.py                 # OTP generation, email sending
│   └── views.py                # All view functions
├── config/                     # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Project settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py
├── templates/
│   └── authentication/         # All HTML templates
│       ├── base.html           # Base template (navbar + footer)
│       ├── home.html
│       ├── register.html
│       ├── admin_login.html
│       ├── distributor_login.html
│       ├── admin_dashboard.html
│       ├── distributor_dashboard.html
│       ├── forgot_password.html
│       ├── verify_otp.html
│       └── reset_password.html
├── static/
│   ├── css/
│   └── js/
├── media/                      # User-uploaded files
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Routes

| Route                        | Description                          |
|------------------------------|--------------------------------------|
| `/`                          | Home page                            |
| `/register/`                 | Distributor registration             |
| `/admin-login/`              | Admin login page                     |
| `/distributor-login/`        | Distributor login page               |
| `/admin-dashboard/`          | Admin dashboard (protected)          |
| `/distributor-dashboard/`    | Distributor dashboard (protected)    |
| `/admin-logout/`             | Admin logout                         |
| `/distributor-logout/`        | Distributor logout                   |
| `/forgot-password/`          | Request OTP for password recovery    |
| `/verify-otp/`               | Verify OTP                           |
| `/reset-password/`           | Set new password after OTP verified  |
| `/admin/`                    | Django admin panel                   |
