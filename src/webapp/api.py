"""Default API configuration."""
from typing import List, Tuple

from django.conf import settings  # type: ignore
from django.urls import include, path  # type: ignore
from rest_auth import urls as rest_auth_urls  # type: ignore
from rest_auth.registration import urls as rego  # type: ignore
from rest_framework import urls as rest_urls  # type: ignore
from rest_framework.documentation import include_docs_urls  # type: ignore
from rest_framework.routers import DefaultRouter  # type: ignore
from rest_framework.viewsets import ViewSetMixin  # type: ignore
from rest_framework_jwt import views as jwt_views  # type: ignore

# Add viewsets here. The first argument is the name and the URL regex
routes: List[Tuple[str, ViewSetMixin]] = [
]  # yapf: disable

v1_router = DefaultRouter()

for regex, viewset in routes:
    v1_router.register(regex, viewset, base_name=regex)


api = [
    path('', include(v1_router.urls)),
    path('', include(rest_urls)),
    path('auth/', include(rest_auth_urls)),
    path('auth/registration/', include(
        rego if settings.ACCOUNT_REGISTRATION.lower() == 'enabled' else []
    )),
    path('auth/token/', include([
        path('obtain/', jwt_views.obtain_jwt_token),
        path('refresh/', jwt_views.refresh_jwt_token),
        path('verify/', jwt_views.verify_jwt_token),
    ])),
    path('docs/', include_docs_urls(title=settings.APP_NAME, public=False)),
]  # yapf: disable
