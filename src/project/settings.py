import os
from pathlib import Path

import dj_database_url
from django.urls import reverse_lazy
from dynaconf import settings as _settings

BASE_DIR = Path(__file__).parent.parent.resolve()
PROJECT_DIR = BASE_DIR / "project"

SECRET_KEY = _settings.SECRET_KEY

DEBUG = _settings.DEBUG

ALLOWED_HOSTS = _settings.ALLOWED_HOSTS

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # DRF
    "rest_framework",
    # our apps
    "apps.about",
    "apps.actual",
    "apps.api",
    "apps.dynamics",
    "apps.graphics",
    "apps.onboarding",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PROJECT_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "project.wsgi.app"

db_url = _settings.DATABASE_URL
if _settings.ENV_FOR_DYNACONF == "heroku":
    db_url = os.getenv("DATABASE_URL")

DATABASES = {"default": dj_database_url.parse(db_url, conn_max_age=600)}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_ROOT_DIR = BASE_DIR / "static"
STATIC_ROOT_DIR.mkdir(exist_ok=True)
STATIC_ROOT = STATIC_ROOT_DIR.as_posix()

STATIC_URL = "/static/"

STATICFILES_DIRS = [PROJECT_DIR / "static"]

# AUTH

LOGIN_URL = reverse_lazy("login")
LOGIN_REDIRECT_URL = reverse_lazy("actual")

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]
