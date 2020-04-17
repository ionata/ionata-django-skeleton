"""Config for the webapp app."""
from django.apps import AppConfig


class WebAppConfig(AppConfig):
    """Config for the webapp app."""

    name = "webapp"

    def ready(self):
        """Import signals."""
        # noqa pylint: disable=unused-import,import-outside-toplevel
        from webapp import signals
