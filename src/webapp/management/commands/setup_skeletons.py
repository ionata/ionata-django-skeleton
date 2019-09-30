"""Management Command to setup initial data."""
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django_celery_beat.models import IntervalSchedule, PeriodicTask


def get_admin():
    """Return the default admin, creating it if not present."""
    admin = settings.ADMIN_USER
    model = get_user_model()
    if model is None:
        raise ImportError("Cannot import the specified User model")
    username = model.USERNAME_FIELD
    restrict = [username, "password"]
    defaults = {x: True for x in ["is_staff", "is_superuser", "is_active"]}
    env_vals = {k: v for k, v in admin.items() if k not in restrict}
    defaults.update(env_vals)
    try:
        values = {username: admin[username], "defaults": defaults}
        user, new = model.objects.get_or_create(**values)
    except IntegrityError:
        raise AttributeError("Admin user not found or able to be created.")
    if new:
        user.set_password(admin["password"])
        user.save()
    return user


def get_site():
    """Return the default site, creating it if not present."""
    url = urlparse(settings.SITE_URL)
    defaults = {"name": settings.PROJECT_NAME, "domain": url.hostname}
    kwargs = {"pk": settings.SITE_ID, "defaults": defaults}
    return Site.objects.get_or_create(**kwargs)[0]


def schedule_check():
    """Schedule celery heartbeat task."""
    interval = IntervalSchedule.objects.get_or_create(every=10, period="minutes")[0]
    PeriodicTask.objects.get_or_create(
        name="send_beat", task="webapp.tasks.send_beat", interval=interval
    )


class Command(BaseCommand):
    """Management command to setup initial data."""

    def handle(self, *args, **options):
        """Run the management command."""
        print(f"Running setup for {settings.PROJECT_NAME}")
        get_admin()
        get_site()
        schedule_check()
