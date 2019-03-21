from django.apps import AppConfig


class WebAppConfig(AppConfig):
    name = 'webapp'

    def ready(self):
        # noqa pylint: disable=unused-import
        from webapp import signals
