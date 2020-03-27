"""Tests for sessions endpoint."""
# pylint: disable=invalid-name
from __future__ import annotations

from hamcrest import instance_of
from rest_framework import status

from users.models import User
from users.tests import factories
from webapp.tests.base import JsonApiTestCase
from webapp.tests.matchers import is_to_one


class SessionsTestCase(JsonApiTestCase):
    """Test validation on sessions endpoint."""

    resource_name: str = "sessions"
    attributes = {"token": instance_of(str)}
    relationships = {"user": is_to_one(resource_name="users")}

    def test_can_create_session(self):
        """Test user can create session."""
        email = "test@example.com"
        password = "hellopass123"
        user = factories.UserFactory(email=email, password=password)
        data = {"data": self.get_data(email=email, password=password)}
        response = self.post(
            f"/{self.resource_name}/",
            data=data,
            asserted_status=status.HTTP_201_CREATED,
            asserted_schema=self.get_schema(),
        )
        json = response.json()
        # check parameters are correct
        self.assertIn("token", json["data"]["attributes"])
        self.assertDictEqual(
            json["data"]["relationships"]["user"], self.get_to_one(user)
        )

    def test_can_get_own_session(self):
        """Test user can get own session."""
        email = "test@example.com"
        password = "hellopass123"
        user = factories.UserFactory(email=email, password=password)
        self.auth(user)
        response = self.get(
            f"/{self.resource_name}/",
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.get_schema(many=True, exclude=["token"]),
        )
        json = response.json()
        # check there is one instance in the json
        self.assertEqual(len(json["data"]), 1)
        session = json["data"][0]
        # check parameters are correct
        self.assertNotIn("token", session["attributes"])
        self.assertDictEqual(session["relationships"]["user"], self.get_to_one(user))

    def test_unauthenticated_user_cannot_get_session(self):
        """Test unauthenticated user cannot get session."""
        response = self.get(
            f"/{self.resource_name}/", asserted_status=status.HTTP_401_UNAUTHORIZED
        )
        json = response.json()
        # check has correct error
        self.assertHasError(
            json, "data", "Authentication credentials were not provided."
        )

    def test_authenticated_user_can_delete_session(self):
        """Test authenticated user can delete session."""
        email = "user@example.com"
        password = "pass"
        factories.UserFactory(email=email, password=password)
        data = {"data": self.get_data(email=email, password=password)}
        token_json = self.post(f"/{self.resource_name}/", data=data).json()
        token = token_json["data"]["attributes"]["token"]
        # check the token is valid
        self.client.credentials(  # pylint: disable=no-member
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.get(
            f"/{self.resource_name}/",
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.get_schema(many=True, exclude=["token"]),
        )
        # delete the token (logout)
        self.delete(
            f"/{self.resource_name}/", asserted_status=status.HTTP_204_NO_CONTENT
        )
        # check the token is no longer valid
        self.get(
            f"/{self.resource_name}/", asserted_status=status.HTTP_401_UNAUTHORIZED
        )

    def test_include_user_fails(self):
        """Test ?include=user results in a validation error."""
        email = "user@example.com"
        password = "pass"
        factories.UserFactory(email=email, password=password)
        data = {"data": self.get_data(email=email, password=password)}
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
