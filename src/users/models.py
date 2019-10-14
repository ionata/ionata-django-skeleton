"""User models."""
from typing import List

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Email and password are required. Other fields are optional."""

    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: List[str] = []

    objects = UserManager()

    class Meta:
        """Model meta options."""

        verbose_name = _("user")
        verbose_name_plural = _("users")
        swappable = "AUTH_USER_MODEL"

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "users"

    def get_full_name(self):
        """Return the email (this method is required)."""
        return self.email

    def get_short_name(self):
        """Return the email (this method is required)."""
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
