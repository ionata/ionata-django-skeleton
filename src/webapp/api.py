"""Default API configuration."""
from typing import List, Tuple

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSetMixin

import users.views
from webapp.views import schema_view

# Add viewsets here. The first argument is the name and the URL regex
routes: List[Tuple[str, ViewSetMixin]] = [
    ("users", users.views.UserView),
    ("sessions", users.views.SessionView),
    ("password-resets", users.views.PasswordResetView),
    ("password-reset-confirmations", users.views.PasswordResetConfirmView),
]

v1_router = DefaultRouter()

for regex, viewset in routes:
    v1_router.register(regex, viewset, basename=regex)


api = [
    path("", include(v1_router.urls)),
    path("schema/", schema_view, name="openapi-schema"),
]
