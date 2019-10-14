"""Project wide tasks."""
import requests
from axes.helpers import get_cache, get_cache_timeout
from celery import shared_task  # pylint: disable=no-name-in-module
from django.conf import settings  # pylint: disable=wrong-import-order
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils.timezone import now


@shared_task
def send_beat():
    """Alert the heartbeat server that celery is running."""
    if not settings.HEARTBEAT_SERVER:
        return
    requests.post(
        f"{settings.HEARTBEAT_SERVER}/api/v1/updates/",
        {"project": settings.PROJECT_NAME, "status": "HEARTBEAT", "task": "send_beat"},
    )


@shared_task
def email_admins_on_user_locked_out(cache_key, ip_address):
    """Email admins on user locked out."""
    cache = get_cache()
    key = f"{cache_key}-notified"
    lockout_email_sent = cache.get(key, False)
    if not lockout_email_sent:
        cache.set(key, True, get_cache_timeout())
        context = {
            "ip_address": ip_address,
            "time": now(),
            "project_name": settings.PROJECT_NAME,
        }
        mail_admins(
            subject="A lockout has occured",
            message=render_to_string("axes/lockout_admin_email.txt", context=context),
            html_message=render_to_string(
                "axes/lockout_admin_email.html", context=context
            ),
        )
