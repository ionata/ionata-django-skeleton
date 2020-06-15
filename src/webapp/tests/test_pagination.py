"""Ensure pagination is enabled."""
import json

from django.test import SimpleTestCase
from hamcrest import all_of, assert_that, has_entry, has_key
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory
from rest_framework_json_api.views import ModelViewSet


class Serializer(serializers.Serializer):
    """Test serializer."""

    def create(self, *args, **kwargs):
        """Override abstract method (although not used in tests)."""

    def update(self, *args, **kwargs):
        """Override abstract method (although not used in tests)."""


class View(ModelViewSet):
    """Test view."""

    permission_classes = [AllowAny]
    serializer_class = Serializer

    def get_queryset(self, *args, **kwargs):
        """Return empty list - we only care that pagination is present."""
        return []


def get_json_from_response(response):
    """Ensure the response is rendered and return the content as json."""
    if not response.is_rendered:
        response.render()
    return json.loads(response.content)


class TestCase(SimpleTestCase):
    """
    Ensure pagiantion is enabled.

    NOTE: These tests assume that the project is configured for JSON:API.
    """

    def test_pagination(self):
        """Results are paginated when specifying params."""
        view = View.as_view({"get": "list"})
        request = APIRequestFactory().get("/", {"page[size]": 10})
        response = view(request)
        # check the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_json = get_json_from_response(response)
        # check the JSON:API pagination params are present
        # https://jsonapi.org/format/#fetching-pagination
        pagination_keys = ["first", "last", "prev", "next"]
        assert_that(
            resp_json,
            has_entry("links", all_of(*[has_key(key) for key in pagination_keys])),
        )

    def test_default_pagination(self):
        """Results are paginated without specifying params."""
        view = View.as_view({"get": "list"})
        request = APIRequestFactory().get("/")
        response = view(request)
        # check the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_json = get_json_from_response(response)
        # check the JSON:API pagination params are present
        # https://jsonapi.org/format/#fetching-pagination
        pagination_keys = ["first", "last", "prev", "next"]
        assert_that(
            resp_json,
            has_entry("links", all_of(*[has_key(key) for key in pagination_keys])),
        )
