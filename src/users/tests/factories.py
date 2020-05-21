"""Factories for users app."""
import factory
from django.contrib.auth.models import Permission

from users import models


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        """Factory meta information."""

        model = models.User
        django_get_or_create = ["email"]

    email = factory.Sequence(lambda n: "user_%04d@example.com" % n)
    password = factory.PostGenerationMethodCall("set_password", "pass")

    @factory.post_generation
    # pylint: disable=unused-argument
    def permission_codes(user, create, extracted, **kwargs):
        """Add permissions to user."""
        if create and extracted:
            for perm in extracted:
                app_label, codename = perm.split(".")
                permission = Permission.objects.filter(
                    content_type__app_label=app_label, codename=codename
                ).first()
                if permission is None:
                    raise factory.errors.FactoryError(
                        f"The permission identified by `{perm}`"
                        " does not exist in the database."
                    )
                user.user_permissions.add(permission)
