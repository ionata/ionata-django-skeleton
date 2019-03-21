import requests
from celery import shared_task  # pylint: disable=no-name-in-module
from django.conf import settings  # pylint: disable=wrong-import-order


@shared_task
def send_beat():
    if not settings.HEARTBEAT_SERVER:
        return
    requests.post(
        f"{settings.HEARTBEAT_SERVER}/api/v1/updates/",
        {"project": settings.APP_NAME, "status": "HEARTBEAT", "task": "send_beat"},
    )
