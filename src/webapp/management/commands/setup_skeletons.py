"""Management Command to setup initial data."""
from enum import Enum
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from webapp.storage import MediaS3


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


def configure_bucket(policy_path: str):
    """Configure the storage bucket."""
    if not isinstance(default_storage, MediaS3):
        return
    ensure_bucket_exists(default_storage)
    create_bucket_policy(default_storage, policy_path)


def ensure_bucket_exists(storage: MediaS3):
    """Ensure the bucket exists."""
    storage.create_bucket()


def create_bucket_policy(storage: MediaS3, policy_path: str):
    """Create a bucket policy."""
    with open(policy_path) as fyl:
        policy = fyl.read()
        storage.bucket.Policy().put(Policy=policy)


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

    def _log(self, message, level=Verbosity.normal, style=None):
        if self.verbosity >= level:
            output = message
            if style is not None:
                output = style(message)
            self.stdout.write(output)

    def add_arguments(self, parser):
        """Add bucket-policy argument."""
        default_path = "/var/www/conf/docker/bucket_policy.json"
        parser.add_argument(
            "--bucket-policy",
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
        self._log(f"Running setup for {settings.PROJECT_NAME}", style=self.style.NOTICE)
        bucket_policy = options["bucket_policy"]
        get_admin()
        get_site()
        is_minio = "minio" in getattr(settings, "AWS_S3_ENDPOINT_URL", "")
        if settings.DEBUG and is_minio:
            configure_bucket(bucket_policy)
        elif not settings.DEBUG:
            self._log(
                "Skipping creating bucket policy since settings.DEBUG is False",
                style=self.style.NOTICE,
            )
        elif not is_minio:
            self._log(
                "Skipping creating bucket policy since "
                'settings.AWS_S3_ENDPOINT_URL does not contain "minio"',
                style=self.style.NOTICE,
            )
