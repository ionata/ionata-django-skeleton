"""Serializers for users app."""
# pylint: disable=abstract-method
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode as b64e
from rest_auth import serializers as auth_serializers
from rest_auth.registration import serializers as rego_serializers
from rest_framework.serializers import ModelSerializer

_user = get_user_model()
USER_FIELDS = list(set(["id", _user.USERNAME_FIELD, _user.EMAIL_FIELD]))

RESET_TEMPLATES = {
    "email_template_name": "registration/password_reset_email.txt",
    "html_email_template_name": "registration/password_reset_email.html",
}


class UserDetailsSerializer(ModelSerializer):
    """Simple user details serializer."""

    class Meta:
        """Serializer Meta information."""

        model = _user
        read_only_fields = fields = USER_FIELDS


class RegisterSerializer(rego_serializers.RegisterSerializer):
    """Signup serializer that removes case."""

    def validate_email(self, email):  # pylint: disable=no-self-use
        """Casefold the email address before validation."""
        return super().validate_email(email.casefold())


class LoginSerializer(auth_serializers.LoginSerializer):
    """Login serializer that removes case."""

    def validate_email(self, value):  # pylint: disable=no-self-use
        """Login serializer that removes case."""
        return value.casefold()


class PasswordResetSerializer(auth_serializers.PasswordResetSerializer):
    """Password reset serializer that removes case."""

    def get_email_context(self):
        """Casefold the email address before encoding it."""
        email = self.data["email"].casefold().encode("utf-8")
        email_encoded = b64e(email)
        # As of Django 2.2 urlsafe_base64_encode returns a str instead of bytes
        # https://github.com/django/django/commit/c82893c
        if isinstance(email_encoded, bytes):
            email_encoded = email_encoded.decode("utf-8")
        return {"email_encoded": email_encoded}

    def get_email_options(self):  # pylint: disable=no-self-use
        """Update email options."""
        return {
            **super().get_email_options(),
            **RESET_TEMPLATES,
            **{"extra_email_context": self.get_email_context()},
        }

    def validate_email(self, value):  # pylint: disable=no-self-use
        """Casefold the email address before validation."""
        return super().validate_email(value.casefold())
