"""Root url config."""
from django.apps import apps  # type: ignore
from django.conf import settings  # type: ignore
from django.contrib import admin  # type: ignore
from django.urls import include, path  # type: ignore


def _static_urls() -> list:
    if not settings.DEBUG:
        return []
    # pylint: disable=import-outside-toplevel
    from django.conf.urls.static import static  # type: ignore
    from django.contrib.staticfiles import urls  # type: ignore

    _static = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    return urls.staticfiles_urlpatterns() + _static


def _djdt_urls() -> list:
    if apps.is_installed("debug_toolbar"):
        import debug_toolbar  # pylint: disable=import-outside-toplevel

        return debug_toolbar.urls
    return []


def _api_urls() -> list:
    if apps.is_installed("rest_framework"):
        from webapp import api  # pylint: disable=import-outside-toplevel

        return api.api
    return []


urlpatterns = [
    path(
        "backend/",
        include(
            [
                path("", include(_static_urls())),
                path("__debug__/", include(_djdt_urls())),
                path("api/v1/", include(_api_urls())),
                path("django-admin/", admin.site.urls),
            ]
        ),
    )
]
