"""Project wide signals."""
# pylint: disable=unused-argument
import requests
from axes.helpers import get_client_cache_key, get_credentials
from axes.signals import user_locked_out
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult

from webapp import tasks


@receiver(user_locked_out)
def email_admins_on_user_locked_out(request, username, ip_address, **kwargs):
    """Email admins on user locked out."""
    tasks.email_admins_on_user_locked_out.apply_async(
        [get_client_cache_key(request, get_credentials(username)), ip_address]
    )


@receiver(post_save, sender=TaskResult, dispatch_uid="heartbeat:taskResult")
def task_result(sender, instance, raw=False, created=False, **kwargs):
    """Alert the heartbeat server that celery is running."""
    if raw or not settings.HEARTBEAT_SERVER:
        return
    requests.post(
        f"{settings.HEARTBEAT_SERVER}/api/v1/updates/",
        {
            "project": settings.PROJECT_NAME,
            "status": instance.status,
            "task": instance.task_name,
        },
    )
