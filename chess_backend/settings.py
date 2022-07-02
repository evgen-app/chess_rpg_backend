import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-%_8sy196w4hzo9^cp9(@r=i+amh47r4mxfhq_(ok&=c(@%bhmk"
TOKEN_EXP = 2678400  # 31 day
DEBUG = True

ALLOWED_HOSTS = []

if DEBUG:
    ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    # Packages
    "rest_framework",
    "channels",
    # Apps
    "game",
    "room",
]

if DEBUG:
    INSTALLED_APPS.append("drf_yasg")


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
            ],
        },
    },
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chess_backend.urls"

ASGI_APPLICATION = "chess_backend.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


WSGI_APPLICATION = "chess_backend.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGES = [
    ("en-us", "English"),
    ("ru", "Russian"),
]

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")
else:
    MEDIA_ROOT = "/var/www/media/"
    STATIC_ROOT = "/var/www/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
