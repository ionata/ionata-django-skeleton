"""Management Command to setup initial data."""
import argparse
from enum import Enum
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from storages.backends.s3boto3 import S3Boto3Storage


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


def create_bucket_policy(fyl):
    """Create a bucket policy."""
    if not isinstance(default_storage, S3Boto3Storage):
        return
    policy = fyl.read()
    default_storage.bucket.Policy().put(Policy=policy)


class Verbosity(Enum):
    """Verbosity enum."""

    minimal = 0
    normal = 1
    verbose = 2
    very_verbose = 3

    def __ge__(self, other):
        """Return true if this instance is greater than or equal to other."""
        if self.__class__ is other.__class__:
            return self.value >= other.value  # pylint: disable=comparison-with-callable
        return NotImplemented

    def __gt__(self, other):
        """Return true if this instance is greater than other."""
        if self.__class__ is other.__class__:
            return self.value > other.value  # pylint: disable=comparison-with-callable
        return NotImplemented

    def __le__(self, other):
        """Return true if this instance is less than or equal to other."""
        if self.__class__ is other.__class__:
            return self.value <= other.value  # pylint: disable=comparison-with-callable
        return NotImplemented

    def __lt__(self, other):
        """Return true if this instance is less than other."""
        if self.__class__ is other.__class__:
            return self.value < other.value  # pylint: disable=comparison-with-callable
        return NotImplemented


class Command(BaseCommand):
    """Management command to setup initial data."""

    def __init__(self, *args, **kwargs):
        """Set default verbosity."""
        super().__init__(*args, **kwargs)
        self.verbosity: Verbosity

    def _log(self, message, level=Verbosity.normal):
        if self.verbosity >= level:
            print(message)

    def add_arguments(self, parser):
        """Add bucket-policy argument."""
        default_path = "/var/www/conf/docker/bucket_policy.json"
        parser.add_argument(
            "--bucket-policy",
            type=argparse.FileType("r"),
            default=default_path,
            help=(
                "The path to the json file that should be used to create "
                "the bucket policy. (Only available when settings.DEBUG "
                f"is True and using minio.) Default: {default_path}"
            ),
        )

    def handle(self, *args, **options):
        """Run the management command."""
        self.verbosity = Verbosity(options["verbosity"])
        self._log(f"Running setup for {settings.PROJECT_NAME}")
        bucket_policy = options["bucket_policy"]
        get_admin()
        get_site()
        schedule_check()
        is_minio = "minio" in getattr(settings, "AWS_S3_ENDPOINT_URL", "")
        if settings.DEBUG and is_minio:
            create_bucket_policy(bucket_policy)
        elif not settings.DEBUG:
            self._log(f"Skipping creating bucket policy since settings.DEBUG is False")
        elif not is_minio:
            self._log(
                "Skipping creating bucket policy since "
                'settings.AWS_S3_ENDPOINT_URL does not contain "minio"'
            )
