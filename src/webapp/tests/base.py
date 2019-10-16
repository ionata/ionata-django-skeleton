"""Project wide base test class."""
from typing import Any, Dict, List, Optional, Tuple, Union

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from hamcrest import any_of, assert_that, empty, has_entries, only_contains
from hamcrest.core.base_matcher import BaseMatcher  # type: ignore
from rest_framework import test
from rest_framework_json_api.utils import get_resource_type_from_instance

from users.models import User
from webapp.tests.matchers import (
    IsJsonApiRelationship,
    IsResourceObject,
    IsToMany,
    IsToOne,
)


class APIClient(test.APIClient):
    """Auto set the base api path."""

    api_base = "/backend/api/v1/"

    def _get_path(self, parsed: Tuple[str, str, str, str, str, str]) -> str:
        path = super()._get_path(parsed)
        if path[0] == "/":
            path = (self.api_base or "") + path[1:]
        return path


class JsonApiTestCase(test.APITestCase):
    """Add shortcuts for authentication tasks."""

    client_class = APIClient
    resource_name: str
    attributes: Dict[str, Any]
    relationships: Dict[str, IsJsonApiRelationship]

    def __init__(self, *args, **kwargs):
        """Set initial value of current_user and current_token."""
        super().__init__(*args, **kwargs)
        self.current_user = None
        self.current_token = None

    @classmethod
    def get_schema(cls, many=False, exclude: List[str] = None) -> Optional[BaseMatcher]:
        """Override to wrap into JSON:API format."""
        exclude = exclude or {}
        schema = IsResourceObject(
            resource_name=cls.resource_name,
            attributes={k: v for k, v in cls.attributes.items() if k not in exclude},
            relationships={
                k: v for k, v in cls.relationships.items() if k not in exclude
            },
        )
        if many:
            schema = only_contains(schema)
        return has_entries({"data": any_of(empty(), schema)})

    @classmethod
    def setUpClass(cls):
        """Set up necessary data for tests."""
        super().setUpClass()
        call_command("setup_skeletons", verbosity=0)

    @classmethod
    def give_user_perm(cls, user: User, perm):  # pylint: disable=no-self-use
        """Assign the given permission to the user."""
        app_label, codename = perm.split(".")
        user.user_permissions.add(
            Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
        )
        user.save()

    @classmethod
    def give_user_group(cls, user, group_name: str):  # pylint: disable=no-self-use
        """Assign the group with the given group_name to the user."""
        user.groups.add(Group.objects.get(name=group_name))

    @classmethod
    def get_id(
        cls, resource_name: str, id: Optional[Any] = None
    ):  # pylint: disable=no-self-use,redefined-builtin
        """Return JSON:API compatible id."""
        data = {"type": resource_name}
        if id is not None:
            data["id"] = str(id)
        return data

    @classmethod
    def get_id_from_model_instance(cls, instance):
        """Return JSON:API compatible id from instance."""
        return cls.get_id(get_resource_type_from_instance(instance), instance.pk)

    @classmethod
    def get_to_one(cls, instance: Any) -> Dict[str, Dict[str, str]]:
        """Return JSON:API compatible `to one`."""
        return {"data": cls.get_id_from_model_instance(instance) if instance else None}

    @classmethod
    def get_to_many(cls, instances: List[Any]) -> Dict[str, List[Dict[str, str]]]:
        """Return JSON:API compatible `to many`."""
        return {
            "data": [
                cls.get_id_from_model_instance(i) for i in instances if i is not None
            ]
        }

    @classmethod
    def get_relationship(cls, name, instance: Union[List[Any], Any]):
        """Get relationship based on name."""
        if isinstance(cls.relationships[name], IsToOne):
            return cls.get_to_one(instance)
        if isinstance(cls.relationships[name], IsToMany):
            return cls.get_to_many(instance)
        class_name = cls.__name__  # pylint
        raise KeyError(
            f'{class_name}.relationships["{name}"] be a instance of IsToOne or IsToMany.'
        )

    @classmethod
    def get_data(
        cls, id: Optional[Any] = None, **kwargs  # pylint: disable=redefined-builtin
    ) -> Dict[str, Any]:
        """Return JSON:API compatible payload."""
        data = cls.get_id(resource_name=cls.resource_name, id=id)
        attributes = {}
        relationships = {}
        for k, v in kwargs.items():
            if k in cls.relationships:
                relationships[k] = cls.get_relationship(k, v)
            else:
                attributes[k] = v
        data["attributes"] = attributes
        data["relationships"] = relationships
        return data

    def auth(self, user: Optional[User], token: Optional[str] = None):
        """Authenticate as the given user."""
        self.current_user = user
        self.current_token = user
        self.client.force_authenticate(user, token)  # pylint: disable=no-member

    def _check_response(
        self,
        response,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
    ):
        if asserted_status is not None:
            self.assertEqual(
                response.status_code,
                asserted_status,
                f"response.status_code != {asserted_status}",
            )
        if asserted_schema is not None:
            assert_that(response.json(), asserted_schema)

    def get(
        self,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.get and check status and/or the schema."""
        response = self.client.get(*args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def post(
        self,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.post and check status and/or the schema."""
        response = self.client.post(*args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def put(
        self,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.put and check status and/or the schema."""
        response = self.client.put(*args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def patch(
        self,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.patch and check status and/or the schema."""
        response = self.client.patch(*args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def delete(
        self,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.delete and check status and/or the schema."""
        response = self.client.delete(*args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

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
