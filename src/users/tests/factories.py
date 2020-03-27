"""Factories for users app."""
import factory


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        """Factory meta information."""

        model = "users.User"
        django_get_or_create = ["email"]

    email = factory.Sequence(lambda n: "user_%04d@example.com" % n)
    password = factory.PostGenerationMethodCall("set_password", "pass")
