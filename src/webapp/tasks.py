"""Project wide tasks."""
from axes.helpers import get_cache, get_cache_timeout
from celery import shared_task
from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils.timezone import now


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
