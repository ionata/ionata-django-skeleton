"""Tests for users app."""
# pylint: disable=invalid-name
from __future__ import annotations

from rest_framework import status

from users.models import User
from webapp.base_test_case import EndpointTestCase


class UsersTestCase(EndpointTestCase):
    """Test validation on users endpoint."""

    resource_name: str = "users"

    def test_can_create_user(self):
        """Test can create users."""
        email = "test@example.com"
        password = "hellopass123"
        data = self.get_data(email=email, password=password)
        response = self.client.post(f"/{self.resource_name}/", data=data)
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
        user = User.objects.create_user(email="user@example.com", password="pass")
        self.auth(user)
        email = "test@example.com"
        password = "hellopass123"
        data = self.get_data(email=email, password=password)
        response = self.client.post(f"/{self.resource_name}/", data=data)
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # check email is correct
        self.assertHasError(json, "data", "You cannot create users.")

    def test_user_with_perms_can_create_user(self):
        """Test authenticated user cannot create user."""
        user = User.objects.create_user(email="user@example.com", password="pass")
        self.give_user_perm(user, "users.add_user")
        self.auth(user)
        self.test_can_create_user()

    def test_user_cannot_get_other_user(self):
        """Test user cannot get other user."""
        user = User.objects.create_user(email="user@example.com", password="pass")
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        self.auth(user)
        response = self.client.get(f"/{self.resource_name}/{other_user.pk}/")
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # check has correct error
        self.assertHasError(json, "detail", "Not found.")

    def test_user_with_perms_can_get_other_user(self):
        """Test user cannot get other user."""
        user = User.objects.create_user(email="user@example.com", password="pass")
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        self.give_user_perm(user, "users.view_user")
        self.auth(user)
        response = self.client.get(f"/{self.resource_name}/{other_user.pk}/")
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check parameters are correct
        self.assertEqual(json["data"]["id"], str(other_user.pk))
        self.assertEqual(json["data"]["attributes"]["email"], other_user.email)

    def test_user_cannot_patch_other_user(self):
        """Test user cannot get other user."""
        password = "pass"
        user = User.objects.create_user(email="user@example.com", password=password)
        other_user = User.objects.create_user(
            email="other@example.com", password=password
        )
        self.auth(user)
        data = self.get_data(
            id=other_user.id, current_password=password, password="hellopass123"
        )
        response = self.client.patch(
            f"/{self.resource_name}/{other_user.pk}/", data=data
        )
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # check has correct error
        self.assertHasError(json, "detail", "Not found.")

    def test_user_can_change_own_password(self):
        """Test user can change their own password."""
        password = "pass"
        new_password = "hellopass123"
        user = User.objects.create_user(email="user@example.com", password=password)
        self.auth(user)
        data = self.get_data(
            id=user.id, current_password=password, password=new_password
        )
        response = self.client.patch(f"/{self.resource_name}/{user.pk}/", data=data)
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check password was successfully updated
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_user_cannot_change_own_password_without_current_password(self):
        """Test user cannot change own password without current password."""
        password = "pass"
        new_password = "hellopass123"
        user = User.objects.create_user(email="user@example.com", password=password)
        self.auth(user)
        data = self.get_data(id=user.id, password=new_password)
        response = self.client.patch(f"/{self.resource_name}/{user.pk}/", data=data)
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # check has correct error
        self.assertHasError(
            json,
            "current_password",
            "This field is required when changing your password.",
        )

    def test_user_cannot_change_own_password_without_correct_current_password(self):
        """Test user cannot change own password without correct current password."""
        password = "pass"
        new_password = "hellopass123"
        user = User.objects.create_user(email="user@example.com", password=password)
        self.auth(user)
        data = self.get_data(
            id=user.id, current_password="wrong pass", password=new_password
        )
        response = self.client.patch(f"/{self.resource_name}/{user.pk}/", data=data)
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # check has correct error
        self.assertHasError(
            json, "current_password", "Your current password is incorrect."
        )

    def test_can_get_own_user(self):
        """Test user can get own user."""
        password = "pass"
        user = User.objects.create_user(email="user@example.com", password=password)
        self.auth(user)
        response = self.client.get(f"/{self.resource_name}/{user.pk}/")
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check parameters are correct
        self.assertEqual(json["data"]["id"], str(user.pk))
        self.assertEqual(json["data"]["attributes"]["email"], user.email)

    def test_can_patch_other_user_with_perms(self):
        """Test user with proper perms can patch other user."""
        password = "pass"
        new_password = "hellopass123"
        user = User.objects.create_user(email="user@example.com", password=password)
        other_user = User.objects.create_user(
            email="other@example.com", password=password
        )
        self.give_user_perm(user, "users.change_user")
        self.auth(user)
        data = self.get_data(
            id=other_user.id, current_password=password, password=new_password
        )
        response = self.client.patch(
            f"/{self.resource_name}/{other_user.pk}/", data=data
        )
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check parameters are correct
        self.assertEqual(json["data"]["id"], str(other_user.pk))
        self.assertEqual(json["data"]["attributes"]["email"], other_user.email)
        # check password was successfully updated
        other_user.refresh_from_db()
        self.assertTrue(other_user.check_password(new_password))

    def test_unauthenticated_user_cannot_delete(self):
        """Test unauthenticated user cannot delete."""
        user = User.objects.create_user(email="user@example.com", password="pass")
        response = self.client.delete(f"/{self.resource_name}/{user.pk}/")
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # check has correct error
        self.assertHasError(json, "data", 'Method "DELETE" not allowed.')

    def test_authenticated_user_cannot_delete_self(self):
        """Test authenticated user cannot delete self."""
        user = User.objects.create_user(email="test@example.com", password="pass")
        self.give_user_perm(user, "users.delete_user")
        self.auth(user)
        response = self.client.delete(f"/{self.resource_name}/{user.pk}/")
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # check has correct error
        self.assertHasError(json, "data", 'Method "DELETE" not allowed.')

    def test_authenticated_user_cannot_delete_other_user(self):
        """Test unauthenticated user cannot delete other user."""
        user = User.objects.create_user(email="test@example.com", password="pass")
        self.auth(user)
        self.test_unauthenticated_user_cannot_delete()

    def test_authenticated_user_with_perms_cannot_delete_other_user(self):
        """Test authenticated user with perms cannot delete other user."""
        user = User.objects.create_user(email="test@example.com", password="pass")
        self.give_user_perm(user, "users.delete_user")
        self.auth(user)
        self.test_unauthenticated_user_cannot_delete()


class SessionsTestCase(EndpointTestCase):
    """Test validation on sessions endpoint."""

    to_ones = ["user"]
    resource_name: str = "sessions"

    def test_can_create_session(self):
        """Test user can create session."""
        email = "test@example.com"
        password = "hellopass123"
        user = User.objects.create_user(email=email, password=password)
        data = self.get_data(email=email, password=password)
        response = self.client.post(f"/{self.resource_name}/", data=data)
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check parameters are correct
        self.assertIn("token", json["data"]["attributes"])
        self.assertDictEqual(
            json["data"]["relationships"]["user"], self.get_to_one(user)
        )

    def test_can_get_own_session(self):
        """Test user can get own session."""
        email = "test@example.com"
        password = "hellopass123"
        user = User.objects.create_user(email=email, password=password)
        self.auth(user)
        response = self.client.get(f"/{self.resource_name}/")
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check there is one instance in the json
        self.assertEqual(len(json["data"]), 1)
        session = json["data"][0]
        # check parameters are correct
        self.assertNotIn("token", session["attributes"])
        self.assertDictEqual(session["relationships"]["user"], self.get_to_one(user))

    def test_unauthenticated_user_cannot_get_session(self):
        """Test unauthenticated user cannot get session."""
        response = self.client.get(f"/{self.resource_name}/")
        json = response.json()
        # check correct response code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # check has correct error
        self.assertHasError(
            json, "data", "Authentication credentials were not provided."
        )

    def test_authenticated_user_can_delete_session(self):
        """Test authenticated user can delete session."""
        email = "user@example.com"
        password = "pass"
        User.objects.create_user(email=email, password=password)
        data = self.get_data(email=email, password=password)
        token_json = self.client.post(f"/{self.resource_name}/", data=data).json()
        token = token_json["data"]["attributes"]["token"]
        # check the token is valid
        self.client.credentials(  # pylint: disable=no-member
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        response = self.client.get(f"/{self.resource_name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # delete the token (logout)
        response = self.client.delete(f"/{self.resource_name}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # check the token is no longer valid
        response = self.client.get(f"/{self.resource_name}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
