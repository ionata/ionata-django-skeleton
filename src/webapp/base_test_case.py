"""Project wide base test class."""
from typing import Any, Dict, List, Tuple

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


class APITestCase(test.APITestCase):
    """Add shortcuts for authentication tasks."""

    client_class = APIClient
    relationships: List[str] = []
    resource_name: str

    @classmethod
    def setUpClass(cls):
        """Set up necessary data for tests."""
        super().setUpClass()
        call_command("setup_skeletons")

    def _auth(self, user: User):
        self.current_user = user
        self.client.force_authenticate(user)

    def _give_user_perm(self, user: User, perm) -> None:
        app_label, codename = perm.split(".")
        user.user_permissions.add(
            Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
        )
        user.save()

    def _give_user_group(self, user, group_name: str) -> None:
        user.groups.add(Group.objects.get(name=group_name))

    def _rel_dict(self, instance: Any) -> Dict[str, Any]:
        return {
            "data": {
                "type": get_resource_type_from_instance(instance),
                "id": str(instance.pk),
            }
            if instance
            else None
        }

    def _data(self, id: int, **kwargs: Any) -> Dict[str, Any]:
        return {
            "data": {
                "id": id,
                "type": self.resource_name,
                "attributes": {
                    arg: kwargs[arg] for arg in kwargs if arg not in self.relationships
                },
                "relationships": {
                    arg: self._rel_dict(kwargs[arg])
                    for arg in kwargs
                    if arg in self.relationships
                },
            }
        }

    def assertHasError(
        self, response: Dict[str, Any], field_name: str, error_msg: str
    ) -> None:
        """Assert that the error message is in the response."""
        if not "errors" in response:
            msg = "Response does not contain 'errors'"
            raise self.failureException(msg)
        for error in response["errors"]:
            if not error["source"]["pointer"].rsplit("/", 1)[-1] == field_name:
                continue
            if error["detail"] == error_msg:
                return
        msg = (
            f"Response does not contain the error: '{error_msg}'"
            f" for the field '{field_name}'"
        )
        raise self.failureException(msg)
