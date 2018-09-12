"""Bootstrap celery with Django's config"""
# pylint: disable=wrong-import-position,wrong-import-order
import os

from celery import Celery  # type: ignore
from django.conf import settings  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

import configurations  # type: ignore # noqa

configurations.setup()

app = Celery(settings.CELERY_APP_NAME)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
