"""Ensure the schema endpoint serves an openapi document."""
from rest_framework import status
from rest_framework.test import APISimpleTestCase

from webapp.test.base import APIClient


class TestCase(APISimpleTestCase):
    """Ensure the schema endpoint serves an openapi document."""

    client_class = APIClient

    def test_schema(self):
        """Ensure the schema endpoint serves an openapi document."""
        response = self.client.get("/schema/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header("Content-Type"))
        self.assertEqual(response["Content-Type"], "application/vnd.oai.openapi")
