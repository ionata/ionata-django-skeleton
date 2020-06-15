"""Tests for sessions endpoint."""
from __future__ import annotations

from rest_framework import status

from users.tests import factories, schemas
from webapp.test.base import JsonApiTestCase


class TestCase(JsonApiTestCase):
    """Test validation on sessions endpoint."""

    schema = schemas.SessionsSchema

    def test_anon_create(self):
        """Unauthenticated user can create session."""
        email = "test@example.com"
        password = "hellopass123"
        user = factories.UserFactory(email=email, password=password)
        data = {"data": self.schema.get_data(email=email, password=password)}
        response = self.post(
            f"/{self.resource_name}/",
            data=data,
            asserted_status=status.HTTP_201_CREATED,
            asserted_schema=self.schema.get_matcher(),
        )
        json = response.json()
        # check parameters are correct
        self.assertIn("token", json["data"]["attributes"])
        self.assertEqual(
            json["data"]["relationships"]["user"]["data"]["id"], str(user.pk)
        )

    def test_user_get_own(self):
        """User can get own session."""
        email = "test@example.com"
        password = "hellopass123"
        user = factories.UserFactory(email=email, password=password)
        self.auth(user)
        response = self.get(
            f"/{self.resource_name}/",
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.schema.get_matcher(many=True, exclude=["token"]),
        )
        json = response.json()
        # check there is one instance in the json
        self.assertEqual(len(json["data"]), 1)
        session = json["data"][0]
        # check parameters are correct
        self.assertNotIn("token", session["attributes"])
        self.assertEqual(session["relationships"]["user"]["data"]["id"], str(user.pk))

    def test_anon_get(self):
        """Unauthenticated user cannot get session."""
        response = self.get(
            f"/{self.resource_name}/", asserted_status=status.HTTP_401_UNAUTHORIZED
        )
        json = response.json()
        # check has correct error
        self.assertHasError(
            json, "data", "Authentication credentials were not provided."
        )

    def test_user_delete(self):
        """User can delete session."""
        email = "user@example.com"
        password = "pass"
        factories.UserFactory(email=email, password=password)
        data = {"data": self.schema.get_data(email=email, password=password)}
        token_json = self.post(f"/{self.resource_name}/", data=data).json()
        token = token_json["data"]["attributes"]["token"]
        # check the token is valid
        self.client.credentials(  # pylint: disable=no-member
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.get(
            f"/{self.resource_name}/",
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.schema.get_matcher(many=True, exclude=["token"]),
        )
        # delete the token (logout)
        self.delete(
            f"/{self.resource_name}/", asserted_status=status.HTTP_204_NO_CONTENT
        )
        # check the token is no longer valid
        self.get(
            f"/{self.resource_name}/", asserted_status=status.HTTP_401_UNAUTHORIZED
        )

    def test_include_user(self):
        """User cannot be included in compound document."""
        email = "user@example.com"
        password = "pass"
        factories.UserFactory(email=email, password=password)
        data = {"data": self.schema.get_data(email=email, password=password)}
        token_json = self.post(f"/{self.resource_name}/", data=data).json()
        token = token_json["data"]["attributes"]["token"]
        # check the token is valid
        self.client.credentials(  # pylint: disable=no-member
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        request = self.get(
            f"/{self.resource_name}/?include=user",
            asserted_status=status.HTTP_400_BAD_REQUEST,
        )
        json = request.json()
        # check has correct error
        self.assertHasError(
            json,
            "data",
            "This endpoint does not support the include parameter for path user",
        )
