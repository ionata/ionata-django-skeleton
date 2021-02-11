from rest_framework import permissions
from rest_framework.schemas import get_schema_view
from rest_framework_json_api.schemas.openapi import SchemaGenerator

schema_view = get_schema_view(
    title="<NAME THE SCHEMA>",
    description="e.g. <SCHEMA OF MY PROJECT>",
    version="1.0.0",
    generator_class=SchemaGenerator,
    permission_classes=[permissions.AllowAny],
)
