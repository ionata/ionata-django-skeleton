"""
Settings for your application.
Uncomment the correct imports for your base, and override as necessary.
"""
from typing import List, Tuple

# from ionata_settings import base
from ionata_settings import drf as base


class Project:
    """Settings unique to your project's base Configuration."""

    APP_NAME = 'webapp'

    @property
    def INSTALLED_APPS(self):  # pylint: disable=invalid-name
        """Add ourselves to the installed apps list."""
        return [
            'webapp',
        ] + super().INSTALLED_APPS  # pylint: disable=no-member


class Dev(Project, base.Dev):
    """Override development settings."""


class Prod(Project, base.Prod):
    """Override production settings."""

    SITE_URL = ''
    ADMINS: List[Tuple[str, str]] = []
    MANAGERS: List[Tuple[str, str]] = []
    ALLOWED_HOSTS: List[str] = []
