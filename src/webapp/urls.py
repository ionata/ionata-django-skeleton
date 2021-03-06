"""Root url config."""
from typing import List, Tuple

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
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


urlpatterns = [
    path(
        "backend/",
        include(
            [
                # these are only added in development
                *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
                path(
                    "api/v1/",
                    include(
                        [
                            *v1_router.urls,
                            path("schema/", schema_view, name="openapi-schema"),
                        ]
                    ),
                ),
                path("django-admin/", admin.site.urls),
            ]
        ),
    )
]
