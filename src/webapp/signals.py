# pylint: disable=unused-argument
import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult


@receiver(post_save, sender=TaskResult, dispatch_uid="heartbeat:taskResult")
def task_result(sender, instance, raw=False, created=False, **kwargs):
    if raw or not settings.HEARTBEAT_SERVER:
        return
    requests.post(
        f"{settings.HEARTBEAT_SERVER}/api/v1/updates/",
        {
            "project": settings.APP_NAME,
            "status": instance.status,
            "task": instance.task_name,
        },
    )
