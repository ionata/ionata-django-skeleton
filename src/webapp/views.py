"""View for openapi schema."""

from rest_framework import permissions
from rest_framework.schemas import get_schema_view
from rest_framework_json_api.schemas.openapi import SchemaGenerator
from webapp import settings

schema_view = get_schema_view(
    title=settings.PROJECT_NAME,
    description=f"Schema of {settings.PROJECT_NAME}",
    version="1.0.0",
    generator_class=SchemaGenerator,
    permission_classes=[permissions.AllowAny],
)
