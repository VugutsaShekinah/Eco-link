"""
Django settings for the ECO-LINK project.

ECO-LINK: A Web-Based Plastic Waste Management System (Riara University, BBIT).
Django 5.2 LTS + PostgreSQL. Environment-specific secrets are read from a
`.env` file (never committed) via python-dotenv, as described in the report's
"Technical Challenges" section (5.3.1).
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the project-root .env file (excluded from Git).
load_dotenv(BASE_DIR / ".env")


def env(key, default=None):
    """Small helper: read an environment variable with an optional default."""
    return os.environ.get(key, default)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY",
    "django-insecure-dev-only-key-change-me-in-production",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", "True") == "True"

ALLOWED_HOSTS = env("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ECO-LINK apps (built milestone by milestone)
    "accounts",
    "hubs",
    "dropoffs",
    "rewards",
    "dashboard",
    "leaderboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecolink.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-level templates directory (base.html, shared partials).
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ecolink.wsgi.application"


# Database — PostgreSQL (report §3.4). Credentials come from .env.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "ecolink_db"),
        "USER": env("DB_USER", "postgres"),
        "PASSWORD": env("DB_PASSWORD", ""),
        "HOST": env("DB_HOST", "127.0.0.1"),
        "PORT": env("DB_PORT", "5432"),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Tell Django to use our custom User model instead of the built-in one.
# MUST be set before the very first migration is run.
AUTH_USER_MODEL = "accounts.User"

# Authentication redirects (used once login/logout views exist).
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# Map Django's message levels onto Bootstrap 5 alert classes
# (Django emits "error", Bootstrap expects "danger").
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {
    message_constants.ERROR: "danger",
}


# Email — console backend in development prints messages to the terminal, so
# manufacturer pickup alerts work without an SMTP server (§5.4.3). Set a real
# SMTP backend via EMAIL_BACKEND in production.
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = "ECO-LINK <noreply@eco-link.co.ke>"


# Internationalization — ECO-LINK operates in Nairobi, Kenya.
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Where `collectstatic` gathers files for production serving (Nginx).
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Production security hardening — only applied when DEBUG is off, so local
# development over http still works (report §3.2.2.5: HTTPS, secure cookies).
if not DEBUG:
    SECURE_SSL_REDIRECT = True            # force HTTPS
    SESSION_COOKIE_SECURE = True          # cookies only over HTTPS
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000        # tell browsers to stay on HTTPS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # Trust the proxy's X-Forwarded-Proto header (Nginx/Gunicorn deployment).
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
