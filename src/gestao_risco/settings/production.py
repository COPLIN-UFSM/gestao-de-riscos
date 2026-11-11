import os
import logging

from django.core.exceptions import ImproperlyConfigured

# Settings modules intentionally re-export the shared base settings.
# pylint: disable=wildcard-import,unused-wildcard-import
from .base import *  # noqa: F403


def required_database_setting(name):
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"The {name} environment variable must be set in production.")
    return value


DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured("The SECRET_KEY environment variable must be set in production.")

database = required_database_setting("DB_DATABASE")
host = required_database_setting("DB_HOST")
port = required_database_setting("DB_PORT")
user = required_database_setting("DB_USERNAME")
password = required_database_setting("DB_PASSWORD")
schema = required_database_setting("DB_SCHEMA")

DATABASES = {
    "default": {
        "ENGINE": "ibm_db_django",
        "NAME": database,
        "DATABASE": database,
        "HOST": host,
        "PORT": port,
        "USER": user,
        "PASSWORD": password,
        "OPTIONS": {
            "dsn": (
                f"DATABASE={database};HOSTNAME={host};PORT={port};"
                f"PROTOCOL=TCPIP;CURRENTSCHEMA={schema};"
            )
        },
        "PCONNECT": True,
    }
}

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set ALLOWED_HOSTS to the production host names.")

FORCE_SCRIPT_NAME = os.environ.get("FORCE_SCRIPT_NAME") or None
STATIC_URL = (
    f"{FORCE_SCRIPT_NAME.rstrip('/')}/static/"
    if FORCE_SCRIPT_NAME
    else "/static/"
)

CSRF_TRUSTED_ORIGINS = [
    "https://proplan.ufsm.br",
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_TZ = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}