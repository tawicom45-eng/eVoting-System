import os
from pathlib import Path
import datetime

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - controlled by environment for deployment
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", os.environ.get("SECRET_KEY", "dev-secret-key"))
# DEBUG should be False in production. Control via env var 'DJANGO_DEBUG'.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',') if os.environ.get('ALLOWED_HOSTS') else ['*']

# Security-related settings (toggleable via DJANGO_SECURE or explicit env vars)
DJANGO_SECURE = os.environ.get('DJANGO_SECURE', 'False').lower() in ('1', 'true', 'yes')
# HSTS: set via SECURE_HSTS_SECONDS or enable with DJANGO_SECURE
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0')) if not DJANGO_SECURE else int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() in ('1', 'true', 'yes')
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'False').lower() in ('1', 'true', 'yes')
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True' if DJANGO_SECURE else 'False').lower() in ('1', 'true', 'yes')
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True' if DJANGO_SECURE else 'False').lower() in ('1', 'true', 'yes')
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True' if DJANGO_SECURE else 'False').lower() in ('1', 'true', 'yes')

# Application definition (minimal for dev)
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Local apps
INSTALLED_APPS += [
    "abac",
    "crispy_forms",
    "widget_tweaks",
    "rest_framework",
    "accounts",
    "elections",
    "voting",
    "notifications",
    "results",
    # Scaffolding apps
    "audit",
    "reports",
    "integrity",
    "ledger",
    "monitoring",
    "disputes",
    "analytics",
    "integrations",
    "offline",
    "posters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # custom middleware for revocation checks
    "accounts.middleware.RevokedAccessTokenMiddleware",
]

# Session idle timeout (seconds). Default 30 minutes for MVP.
SESSION_IDLE_TIMEOUT = int(os.environ.get('SESSION_IDLE_TIMEOUT', 1800))

# Add session timeout middleware after AuthenticationMiddleware
MIDDLEWARE.insert(MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware') + 1, 'accounts.middleware.SessionIdleTimeoutMiddleware')

ROOT_URLCONF = "evoting_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "evoting_system.wsgi.application"
ASGI_APPLICATION = "evoting_system.asgi.application"

# Database - use SQLite for local development
# Database configuration: prefer PostgreSQL when environment variables are present,
# otherwise fall back to SQLite for local development.
if os.environ.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "db"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Vote encryption key settings
VOTE_KEYS_DIR = str(BASE_DIR / "keys")
VOTE_PRIVATE_KEY_FILE = "private_key.pem"
VOTE_PUBLIC_KEY_FILE = "public_key.pem"
# Tally signing key settings (used to sign encrypted payloads and verify signatures at tally time)
TALLY_PRIVATE_KEY_FILE = "tally_sign_private.pem"
TALLY_PUBLIC_KEY_FILE = "tally_sign_public.pem"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Access token signing secret (use a secure value in prod, e.g., from KMS)
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET", "dev-access-secret")

# REST framework: add our JTI authentication backend
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "accounts.authentication.JTIAuthentication",
    ],
}

# Media / storage configuration: enable S3-backed media when env vars present
if os.environ.get('AWS_STORAGE_BUCKET_NAME'):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', None)
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', None)
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    # optional: use unsigned URLs OR set MEDIA_URL explicitly
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Site URL for QR generation and absolute links
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# Optional Sentry integration
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()], traces_sample_rate=0.1)
    except Exception:
        # don't block startup if sentry not installed
        pass
