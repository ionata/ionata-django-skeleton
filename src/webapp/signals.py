"""Project wide signals."""
# pylint: disable=unused-argument
from axes.helpers import get_client_cache_key, get_credentials
from axes.signals import user_locked_out
from django.dispatch import receiver

from webapp import tasks


@receiver(user_locked_out)
def email_admins_on_user_locked_out(request, username, ip_address, **kwargs):
    """Email admins on user locked out."""
    tasks.email_admins_on_user_locked_out.apply_async(
        [get_client_cache_key(request, get_credentials(username)), ip_address]
    )
