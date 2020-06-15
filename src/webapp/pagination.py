"""Project-wide pagination classes."""
from rest_framework_json_api import pagination


class JsonApiPageNumberPagination(pagination.JsonApiPageNumberPagination):
    """Increase the max page size."""

    max_page_size = 10000
