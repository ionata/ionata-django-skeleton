"""Tests for users endpoint."""
# pylint: disable=invalid-name
from __future__ import annotations

from rest_framework import status

from users.models import User
from users.tests import factories, schemas
from webapp.tests.base import JsonApiTestCase


class UsersTestCase(JsonApiTestCase):
    """Test validation on users endpoint."""

    schema = schemas.UsersSchema

    def test_can_create_user(self):
        """Test can create users."""
        email = "test@example.com"
        password = "hellopass123"
        data = {"data": self.schema.get_data(email=email, password=password)}
        response = self.post(
            f"/{self.resource_name}/",
            data=data,
            asserted_status=status.HTTP_201_CREATED,
            asserted_schema=self.schema.get_matcher(),
        )
        json = response.json()
        # check email is correct
        self.assertEqual(json["data"]["attributes"]["email"], email)
        # check the id is set
        self.assertIsInstance(json["data"]["id"], str)
        user = User.objects.get(id=json["data"]["id"])
        # check the was correctly hashed and set
        self.assertTrue(user.check_password(password))

    def test_authenticated_user_cannot_create_user(self):
        """Test authenticated user cannot create user."""
        user = factories.UserFactory()
        self.auth(user)
        email = "test@example.com"
        password = "hellopass123"
        data = {"data": self.schema.get_data(email=email, password=password)}
        response = self.post(
            f"/{self.resource_name}/",
            data=data,
            asserted_status=status.HTTP_403_FORBIDDEN,
        )
        json = response.json()
        # check email is correct
        self.assertHasError(json, "data", "You cannot create users.")

    def test_user_with_perms_can_create_user(self):
        """Test authenticated user cannot create user."""
        user = factories.UserFactory(permission_codes=["users.add_user"])
        self.auth(user)
        self.test_can_create_user()

    def test_user_cannot_get_other_user(self):
        """Test user cannot get other user."""
        user, other_user = factories.UserFactory.create_batch(size=2)
        self.auth(user)
        response = self.get(
            f"/{self.resource_name}/{other_user.pk}/",
            asserted_status=status.HTTP_404_NOT_FOUND,
        )
        json = response.json()
        # check has correct error
        self.assertHasError(json, "", "Not found.")

    def test_user_with_perms_can_get_other_user(self):
        """Test user cannot get other user."""
        user = factories.UserFactory(permission_codes=["users.view_user"])
        other_user = factories.UserFactory()
        self.auth(user)
        response = self.get(
            f"/{self.resource_name}/{other_user.pk}/",
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.schema.get_matcher(),
        )
        json = response.json()
        # check parameters are correct
        self.assertEqual(json["data"]["id"], str(other_user.pk))
        self.assertEqual(json["data"]["attributes"]["email"], other_user.email)

    def test_user_cannot_patch_other_user(self):
        """Test user cannot update other users."""
        password = "pass"
        user, other_user = factories.UserFactory.create_batch(password=password, size=2)
        self.auth(user)
        data = {
            "data": self.schema.get_data(
                id=other_user.id, current_password=password, password="hellopass123"
            )
        }
        response = self.patch(
            f"/{self.resource_name}/{other_user.pk}/",
            data=data,
            asserted_status=status.HTTP_404_NOT_FOUND,
        )
        json = response.json()
        # check has correct error
        self.assertHasError(json, "", "Not found.")

    def test_user_can_change_own_password(self):
        """Test user can change their own password."""
        password = "pass"
        new_password = "hellopass123"
        user = factories.UserFactory(email="user@example.com", password=password)
        self.auth(user)
        data = {
            "data": self.schema.get_data(
                id=user.id, current_password=password, password=new_password
            )
        }
        self.patch(
            f"/{self.resource_name}/{user.pk}/",
            data=data,
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.schema.get_matcher(),
        )
        # check password was successfully updated
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_user_cannot_change_own_password_without_current_password(self):
        """Test user cannot change own password without current password."""
        password = "pass"
        new_password = "hellopass123"
        user = factories.UserFactory(password=password)
        self.auth(user)
        data = {"data": self.schema.get_data(id=user.id, password=new_password)}
        response = self.patch(
            f"/{self.resource_name}/{user.pk}/",
            data=data,
            asserted_status=status.HTTP_400_BAD_REQUEST,
        )
        json = response.json()
        # check has correct error
        self.assertHasError(
            json,
            "current_password",
            "This field is required when changing your password.",
        )

    def test_user_cannot_change_own_password_without_correct_current_password(self):
        """Test user cannot change own password without correct current password."""
        new_password = "hellopass123"
        user = factories.UserFactory()
        self.auth(user)
        data = {
            "data": self.schema.get_data(
                id=user.id, current_password="wrong pass", password=new_password
            )
        }
        response = self.patch(
            f"/{self.resource_name}/{user.pk}/",
            data=data,
            asserted_status=status.HTTP_400_BAD_REQUEST,
        )
        json = response.json()
        # check has correct error
        self.assertHasError(
            json, "current_password", "Your current password is incorrect."
        )

    def test_can_get_own_user(self):
        """Test user can get own user."""
        user = factories.UserFactory()
        self.auth(user)
        response = self.get(
            f"/{self.resource_name}/{user.pk}/",
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.schema.get_matcher(),
        )
        json = response.json()
        # check parameters are correct
        self.assertEqual(json["data"]["id"], str(user.pk))
        self.assertEqual(json["data"]["attributes"]["email"], user.email)

    def test_can_patch_other_user_with_perms(self):
        """Test user with proper perms can patch other user."""
        password = "pass"
        new_password = "hellopass123"
        user = factories.UserFactory(permission_codes=["users.change_user"])
        other_user = factories.UserFactory()
        self.auth(user)
        data = {
            "data": self.schema.get_data(
                id=other_user.id, current_password=password, password=new_password
            )
        }
        response = self.patch(
            f"/{self.resource_name}/{other_user.pk}/",
            data=data,
            asserted_status=status.HTTP_200_OK,
            asserted_schema=self.schema.get_matcher(),
        )
        json = response.json()
        # check parameters are correct
        self.assertEqual(json["data"]["id"], str(other_user.pk))
        self.assertEqual(json["data"]["attributes"]["email"], other_user.email)
        # check password was successfully updated
        other_user.refresh_from_db()
        self.assertTrue(other_user.check_password(new_password))

    def test_unauthenticated_user_cannot_delete(self):
        """Test unauthenticated user cannot delete."""
        user = factories.UserFactory()
        response = self.delete(
            f"/{self.resource_name}/{user.pk}/",
            asserted_status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        json = response.json()
        # check has correct error
        self.assertHasError(json, "data", 'Method "DELETE" not allowed.')

    def test_authenticated_user_cannot_delete_self(self):
        """Test authenticated user cannot delete self."""
        user = factories.UserFactory(permission_codes=["users.delete_user"])
        self.auth(user)
        response = self.delete(
            f"/{self.resource_name}/{user.pk}/",
            asserted_status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        json = response.json()
        # check has correct error
        self.assertHasError(json, "data", 'Method "DELETE" not allowed.')

    def test_authenticated_user_cannot_delete_other_user(self):
        """Test unauthenticated user cannot delete other user."""
        user = factories.UserFactory()
        self.auth(user)
        self.test_unauthenticated_user_cannot_delete()

    def test_authenticated_user_with_perms_cannot_delete_other_user(self):
        """Test authenticated user with perms cannot delete other user."""
        user = factories.UserFactory(permission_codes=["users.delete_user"])
        self.auth(user)
        self.test_unauthenticated_user_cannot_delete()
