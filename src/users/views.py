"""Views for the users app."""
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_auth import views as auth_views
from rest_framework import mixins, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSetMixin
from rest_framework_json_api.views import (
    AutoPrefetchMixin,
    PreloadIncludesMixin,
    RelatedMixin,
)

from users.models import User
from users.serializers import SessionSerializer, UserSerializer

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password", "current_password")
)


class _Session:
    def __init__(self, request):
        self.user = request.user
        self.pk = request.user.pk  # pylint: disable=invalid-name


class SessionView(ViewSetMixin, auth_views.LoginView):
    """ViewSet for sessions endpoint."""

    resource_name = "sessions"

    def check_authentication(self, request):
        """Raise NotAuthenticated exception if not authenticated."""
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

    # pylint: disable=unused-argument
    def delete(self, request, *args, **kwargs):
        """Logout on delete."""
        self.check_authentication(request)
        auth_views.LogoutView().logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # pylint: disable=unused-argument
    def list(self, request, *args, **kwargs):
        """Return the session information."""
        self.check_authentication(request)
        serializer = SessionSerializer(
            context={"request": request, "view": self},
            instance=[_Session(request)],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Replace the response status code with 201."""
        response = super().post(request, *args, **kwargs)
        response.status_code = status.HTTP_201_CREATED
        return response


class UserView(
    AutoPrefetchMixin,
    PreloadIncludesMixin,
    RelatedMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """ViewSet for the users endpoint."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    ordering = ["pk"]

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        """Hide sensitive post parameters from the logging."""
        return super().dispatch(request, *args, **kwargs)

    @property
    def is_get(self):
        """Return whether this is a getting action."""
        return self.action in ["list", "retrieve"]

    @property
    def is_update(self):
        """Return whether this is an updatting action."""
        return self.action in ["update", "partial_update"]

    def get_queryset(self, *args, **kwargs):
        """Filter queryset to users based on permissions."""
        qs = super().get_queryset(*args, **kwargs)
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if self.is_get and not user.has_perm("users.view_user"):
            return qs.filter(pk=user.pk)
        if self.is_update and not user.has_perm("users.change_user"):
            return qs.filter(pk=user.pk)
        return qs

    def create(self, request, *args, **kwargs):
        """Prevent creation by authenticated users without perms."""
        user = request.user
        if user.is_authenticated and not user.has_perm("users.add_user"):
            self.permission_denied(request, message=_("You cannot create users."))
        return super().create(request, *args, **kwargs)


class PasswordResetView(
    mixins.CreateModelMixin, ViewSetMixin, auth_views.PasswordResetView
):
    """Request a password reset email."""

    def post(self, request, *args, **kwargs):
        """Use the serializer to get the response."""
        return super().create(*args, **kwargs)


class PasswordResetConfirmView(
    mixins.CreateModelMixin, ViewSetMixin, auth_views.PasswordResetConfirmView
):
    """Reset the password for a user."""

    resource_name = "password-reset-confirmations"

    def post(self, request, *args, **kwargs):
        """Use the serializer to get the response."""
        return super().create(request, *args, **kwargs)
