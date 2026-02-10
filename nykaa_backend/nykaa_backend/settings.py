"""
Django settings for nykaa_backend project.
Production-ready but still works in local.
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env only if variables are not already provided
if not os.getenv("SECRET_KEY"):
    load_dotenv()


# =========================================================
# BASE
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost"
).split(",")


# =========================================================
# APPLICATIONS
# =========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',

    'frontend_app',
    'accounts',
    'products',
    'cart',
    'orders',
    'payments',
    'wishlist',
    'addresses',
    'checkout',
]


# =========================================================
# MIDDLEWARE
# =========================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================================================
# URL / TEMPLATES
# =========================================================
ROOT_URLCONF = 'nykaa_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.bag_count',
                'products.context_processors.header_categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'nykaa_backend.wsgi.application'


# =========================================================
# DATABASE (SAFE)
# =========================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "nykaa_shop"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

AUTH_USER_MODEL = "accounts.User"


# =========================================================
# PASSWORD VALIDATION
# =========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================================================
# INTERNATIONAL
# =========================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =========================================================
# STATIC / MEDIA
# =========================================================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'frontend_app' / 'static'
]

# Needed for production servers
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================
# DEFAULT PK
# =========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================================================
# EMAIL
# =========================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# =========================================================
# DRF + JWT
# =========================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# =========================================================
# RAZORPAY
# =========================================================
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")




# Allow Django to serve media in container (temporary until nginx)
if not DEBUG:
    from django.conf.urls.static import static


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "nykaa_shop"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", "9019860150"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
    }
}

