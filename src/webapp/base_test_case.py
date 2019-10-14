"""Project wide base test class."""
from typing import Any, Dict, List, Optional, Tuple, Union

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from rest_framework import test
from rest_framework_json_api.utils import get_resource_type_from_instance

from users.models import User


class APIClient(test.APIClient):
    """Auto set the base api path."""

    api_base = "/backend/api/v1/"

    def _get_path(self, parsed: Tuple[str, str, str, str, str, str]) -> str:
        path = super()._get_path(parsed)
        if path[0] == "/":
            path = (self.api_base or "") + path[1:]
        return path


class EndpointTestCase(test.APITestCase):
    """Add shortcuts for authentication tasks."""

    client_class = APIClient
    to_ones: List[str] = []
    to_manies: List[str] = []
    resource_name: str

    def __init__(self, *args, **kwargs):
        """Set initial value of current_user and current_token."""
        super().__init__(*args, **kwargs)
        self.current_user = None
        self.current_token = None

    @classmethod
    def get_relationships_list(cls):
        """Return all relationships."""
        return cls.to_ones + cls.to_manies

    @classmethod
    def setUpClass(cls):
        """Set up necessary data for tests."""
        super().setUpClass()
        call_command("setup_skeletons", verbosity=0)

    def auth(self, user: Optional[User], token: Optional[str] = None):
        """Authenticate as the given user."""
        self.current_user = user
        self.current_token = user
        self.client.force_authenticate(user, token)  # pylint: disable=no-member

    def give_user_perm(self, user: User, perm):  # pylint: disable=no-self-use
        """Assign the given permission to the user."""
        app_label, codename = perm.split(".")
        user.user_permissions.add(
            Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
        )
        user.save()

    def give_user_group(self, user, group_name: str):  # pylint: disable=no-self-use
        """Assign the group with the given group_name to the user."""
        user.groups.add(Group.objects.get(name=group_name))

    @property
    def relationships(self):
        """Return all relationships."""
        return self.get_relationships_list()

    def get_id(
        self, resource_name: str, id: Optional[Any] = None
    ):  # pylint: disable=no-self-use,redefined-builtin
        """Return JSON:API compatible id."""
        data = {"type": resource_name}
        if id is not None:
            data["id"] = str(id)
        return data

    def get_id_from_model_instance(self, instance):
        """Return JSON:API compatible id from instance."""
        return self.get_id(get_resource_type_from_instance(instance), instance.pk)

    def get_to_one(self, instance: Any) -> Dict[str, Dict[str, str]]:
        """Return JSON:API compatible `to one`."""
        return {"data": self.get_id_from_model_instance(instance) if instance else None}

    def get_to_many(self, instances: List[Any]) -> Dict[str, List[Dict[str, str]]]:
        """Return JSON:API compatible `to many`."""
        return {
            "data": [
                self.get_id_from_model_instance(i) for i in instances if i is not None
            ]
        }

    def get_relationship(self, name, instance: Union[List[Any], Any]):
        """Get relationship based on name."""
        if name in self.to_ones:
            return self.get_to_one(instance)
        if name in self.to_manies:
            return self.get_to_many(instance)
        class_name = self.__class__.__name__
        raise AssertionError(
            f"{name} must be in {class_name}.to_ones or {class_name}.to_manies"
        )

    def get_data(
        self, id: Optional[Any] = None, **kwargs  # pylint: disable=redefined-builtin
    ) -> Dict[str, Any]:
        """Return JSON:API compatible payload."""
        data = self.get_id(resource_name=self.resource_name, id=id)
        data["attributes"] = {
            k: v for k, v in kwargs.items() if k not in self.relationships
        }
        data["relationships"] = {
            k: self.get_relationship(k, v)
            for k, v in kwargs.items()
            if k in self.relationships
        }
        return {"data": data}

    def assertHasError(
        self, json: Dict[str, Any], field_name: str, error_msg: str
    ):  # pylint: disable=invalid-name
        """Assert that the error message is in the json."""
        if not "errors" in json:
            msg = "json does not contain 'errors'"
            raise self.failureException(msg)
        for error in json["errors"]:
            if not error["source"]["pointer"].rsplit("/", 1)[-1] == field_name:
                continue
            if error["detail"] == error_msg:
                return
        msg = (
            f"json does not contain the error: '{error_msg}'"
            f" for the field '{field_name}'"
        )
        raise self.failureException(msg)
