"""
📦 identiflow_backend/settings.py

🧠 CENTRAL CONFIGURATION SYSTEM

This file controls:
✔ Security
✔ Database
✔ Authentication
✔ Logging (Observability)
✔ AI-ready configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DESIGN PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Environment-aware (dev vs prod)
✔ Modular & scalable
✔ AI & analytics ready
✔ Secure by design
"""

from pathlib import Path
import os
from datetime import timedelta


# =========================================================
# 📁 BASE DIRECTORY
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# 🔐 SECURITY CONFIG
# =========================================================
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-key"  # ⚠️ Replace in production
)

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")


# =========================================================
# 📦 APPLICATIONS
# =========================================================
INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'drf_spectacular',

    # Local apps
    'documents',
]


# =========================================================
# 🔄 MIDDLEWARE
# =========================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # 🔐 Security
    'django.middleware.csrf.CsrfViewMiddleware',

    # Auth
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================================================
# 🌐 URL CONFIG
# =========================================================
ROOT_URLCONF = 'identiflow_backend.urls'


# =========================================================
# 🎨 TEMPLATES
# =========================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# =========================================================
# 🚀 WSGI
# =========================================================
WSGI_APPLICATION = 'identiflow_backend.wsgi.application'


# =========================================================
# 🗄️ DATABASE
# =========================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================================================
# 🔐 PASSWORD VALIDATION
# =========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================================================
# 🌍 INTERNATIONALIZATION
# =========================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True


# =========================================================
# 📦 STATIC & MEDIA FILES
# =========================================================
STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================
# 🔑 DEFAULT PRIMARY KEY
# =========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================================================
# 🔐 DJANGO REST FRAMEWORK
# =========================================================
REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    # Schema (Swagger)
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# =========================================================
# 🔐 JWT CONFIGURATION
# =========================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=4),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# =========================================================
# 📊 API DOCUMENTATION
# =========================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'IdentiFlow API',
    'DESCRIPTION': 'AI-powered secure document intelligence system',
    'VERSION': '1.0.0',
}


# =========================================================
# 🧠 LOGGING SYSTEM (OBSERVABILITY CORE)
# =========================================================
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "detailed": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname}: {message}",
            "style": "{",
        },
    },

    "handlers": {
        # 📁 FILE LOGS (persistent history)
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "identiflow.log",
            "formatter": "detailed",
        },

        # 🖥️ CONSOLE LOGS (live debugging)
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },

    "loggers": {
        "identiflow": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}


# =========================================================
# 🧠 AI / SYSTEM SETTINGS (FUTURE CONTROL LAYER)
# =========================================================
AI_SETTINGS = {
    "DEFAULT_CONFIDENCE_THRESHOLD": 0.85,
    "ENABLE_AI": True,
    "LOG_AI_USAGE": True,
}