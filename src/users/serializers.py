"""Serializers for users app."""
# pylint: disable=abstract-method
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.http import urlsafe_base64_encode as b64e
from django.utils.translation import ugettext_lazy as _
from rest_auth import serializers as auth_serializers
from rest_framework.exceptions import ValidationError
from rest_framework_json_api import serializers

from users.models import User

RESET_TEMPLATES = {
    "email_template_name": "registration/password_reset_email.txt",
    "html_email_template_name": "registration/password_reset_email.html",
}


class _UuidPk:
    def __init__(self):
        self.pk = str(uuid4())  # pylint: disable=invalid-name


class SessionSerializer(
    serializers.IncludedResourcesValidationMixin,
    serializers.SparseFieldsetsMixin,
    serializers.Serializer,
):
    """Session serializer."""

    user = serializers.ResourceRelatedField(model=User, read_only=True)

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "sessions"


class TokenSerializer(
    serializers.IncludedResourcesValidationMixin,
    serializers.SparseFieldsetsMixin,
    auth_serializers.TokenSerializer,
):
    """Set the pk of the instance to be the user's pk."""

    token = serializers.CharField(read_only=True, source="_backup_key")
    user = serializers.ResourceRelatedField(read_only=True)

    class Meta(auth_serializers.TokenSerializer.Meta):
        """Serializer meta information."""

        fields = ["token", "user"]

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "sessions"

    def __init__(self, *args, **kwargs):
        """Set the pk of the instance to be the user's pk."""
        super().__init__(*args, **kwargs)
        if getattr(self, "instance", None):
            self.instance._backup_key = self.instance.pk
            self.instance.pk = self.context["request"].user.pk


class LoginSerializer(
    serializers.IncludedResourcesValidationMixin,
    serializers.SparseFieldsetsMixin,
    auth_serializers.LoginSerializer,
):
    """Login serializer that removes case."""

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "sessions"

    def validate_email(self, value):  # pylint: disable=no-self-use
        """Login serializer that removes case."""
        return value.casefold()


class PasswordResetSerializer(
    serializers.IncludedResourcesValidationMixin,
    serializers.SparseFieldsetsMixin,
    auth_serializers.PasswordResetSerializer,
):
    """Password reset serializer that removes case."""

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "password-resets"

    def get_email_context(self):
        """Casefold the email address before encoding it."""
        email = self.data["email"].casefold().encode("utf-8")
        email_encoded = b64e(email)
        # As of Django 2.2 urlsafe_base64_encode returns a str instead of bytes
        # https://github.com/django/django/commit/c82893c
        if isinstance(email_encoded, bytes):
            email_encoded = email_encoded.decode("utf-8")
        return {"email_encoded": email_encoded, "project_name": settings.PROJECT_NAME}

    def get_email_options(self):
        """Update email options."""
        return {
            **super().get_email_options(),
            **RESET_TEMPLATES,
            **{"extra_email_context": self.get_email_context()},
        }

    def validate_email(self, value):
        """Casefold the email address before validation."""
        return super().validate_email(value.casefold())

    def save(self):
        """Add an instance with a pk for the json api renderer."""
        super().save()
        if getattr(self, "instance", None) is None:
            self.instance = _UuidPk()


class PasswordResetConfirmSerializer(
    serializers.IncludedResourcesValidationMixin,
    serializers.SparseFieldsetsMixin,
    auth_serializers.PasswordResetConfirmSerializer,
):
    """Make the fields write only."""

    new_password1 = serializers.CharField(write_only=True, max_length=128)
    new_password2 = serializers.CharField(write_only=True, max_length=128)
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "password-reset-confirmations"

    def save(self):
        """Add an instance with a pk for the json api renderer."""
        to_return = super().save()
        if getattr(self, "instance", None) is None:
            self.instance = _UuidPk()
        return to_return


class UserSerializer(serializers.ModelSerializer):
    """Users serializer."""

    current_password = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        """Serializer meta information."""

        model = User
        fields = ["email", "password", "current_password"]

    def create(self, validated_data):
        """Create the user with the given email and password."""
        user = User.objects.create_user(
            validated_data["email"], validated_data["password"]
        )
        return user

    def update(self, instance, validated_data):
        """Set the password on the instance."""
        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))
        return super().update(instance, validated_data)

    def validate(self, attrs):
        """Validate data."""
        attrs = super().validate(attrs)
        # creating
        if self.instance is None:
            if "password" not in attrs:
                msg = _("This field is required when creating a new user.")
                raise ValidationError({"password": msg})
        # updating
        else:
            # cannot update email address
            attrs.pop("email", None)
            # when changing password validate current_password
            if "password" in attrs:
                if "current_password" not in attrs:
                    msg = _("This field is required when changing your password.")
                    raise ValidationError({"current_password": msg})
                if not self.instance.check_password(attrs["current_password"]):
                    msg = _("Your current password is incorrect.")
                    raise ValidationError({"current_password": msg})
        # validate the password if it is included
        if "password" in attrs:
            self._validate_password(attrs["password"])
        return attrs

    def _validate_password(self, password):  # pylint: disable=no-self-use
        try:
            validate_password(password)
        except DjangoValidationError as error:
            raise ValidationError({"password": error.messages})
