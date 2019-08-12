"""
Settings for your application.
Uncomment the correct imports for your base, and override as necessary.
"""
from typing import List, Optional, Tuple

# from ionata_settings import base
from ionata_settings import drf as base


class Project:
    """Settings unique to your project's base Configuration."""

    APP_NAME = 'webapp'
    HEARTBEAT_SERVER: Optional[str] = None

    @property
    def INSTALLED_APPS(self):  # pylint: disable=invalid-name
        """Add ourselves to the installed apps list."""
        return [
            'webapp',
        ] + super().INSTALLED_APPS  # pylint: disable=no-member

    # pylint: disable=invalid-name,no-member
    @property
    def CORS_ORIGIN_WHITELIST(self):
        return [item for item in self.ALLOWED_HOSTS if item != '*']

    REST_FRAMEWORK = {
        **base.DRF.REST_FRAMEWORK,
        **{
            'DEFAULT_FILTER_BACKENDS': [
                'rest_framework_filters.backends.RestFrameworkFilterBackend',
            ]
        }
    }


class Dev(Project, base.Dev):
    """Override development settings."""


class Prod(Project, base.Prod):
    """Override production settings."""

    SITE_URL = ''
    HEARTBEAT_SERVER = "https://heartbeat.ionata.com.au"
    ADMINS: List[Tuple[str, str]] = []
    MANAGERS: List[Tuple[str, str]] = []
    ALLOWED_HOSTS: List[str] = []
