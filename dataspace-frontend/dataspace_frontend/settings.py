import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-standalone-dataspace-frontend")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["*"]

# No Django auth/sessions/admin here on purpose - this standalone app doesn't
# have its own user accounts. Authentication is entirely client-side: the
# browser logs into the FastAPI gateway directly and holds the token itself.
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "dataspace",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "dataspace_frontend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "dataspace_frontend.wsgi.application"

# No models/migrations in this project - this default is only here because
# Django's settings module requires a DATABASES entry to exist.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "dataspace" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Base URL of the EnergyGuard Data Space FastAPI gateway. The browser calls
# this directly (CORS is enabled on the gateway) - Django never proxies
# dataspace API calls, it only serves the themed page shell.
DATASPACE_GATEWAY_URL = os.environ.get("DATASPACE_GATEWAY_URL", "http://localhost:8000")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
