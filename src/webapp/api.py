"""Default API configuration."""
from typing import List, Tuple

from django.urls import include, path  # type: ignore
from rest_framework.routers import DefaultRouter  # type: ignore
from rest_framework.viewsets import ViewSetMixin  # type: ignore

from users import views as user_views  # type: ignore

# Add viewsets here. The first argument is the name and the URL regex
routes: List[Tuple[str, ViewSetMixin]] = [
    ("users", user_views.UserView),
    ("sessions", user_views.SessionView),
    ("password-resets", user_views.PasswordResetView),
    ("password-reset-confirmations", user_views.PasswordResetConfirmView),
]

v1_router = DefaultRouter()

for regex, viewset in routes:
    v1_router.register(regex, viewset, basename=regex)


api = [path("", include(v1_router.urls))]
