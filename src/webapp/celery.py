"""Bootstrap celery with Django's config."""
from celery import Celery
from django.conf import settings

app = Celery(settings.CELERY_APP_NAME)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
