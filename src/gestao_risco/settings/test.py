"""Test settings using an isolated, in-memory SQLite database."""

# Settings modules intentionally re-export the shared base settings.
# pylint: disable=wildcard-import,unused-wildcard-import
from .base import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
