"""Local development settings using a persistent SQLite database."""

# Settings modules intentionally re-export the shared base settings.
# pylint: disable=wildcard-import,unused-wildcard-import
from .base import *  # noqa: F403

DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dev.sqlite3",  # noqa: F405
    }
}
