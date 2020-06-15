"""Project wide base test class."""
from typing import Any, Dict, Optional, Tuple, Type

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from hamcrest import assert_that
from hamcrest.core.base_matcher import BaseMatcher  # type: ignore
from rest_framework import status, test

from users.models import User
from webapp.test.schemas import JsonApiSchema


class APIClient(test.APIClient):
    """Auto set the base api path."""

    api_base = "/backend/api/v1/"

    def _get_path(self, parsed: Tuple[str, str, str, str, str, str]) -> str:
        path = super()._get_path(parsed)
        if path[0] == "/":
            path = (self.api_base or "") + path[1:]
        return path


class BaseTestCase(test.APITestCase):
    """Add helper methods."""

    client_class = APIClient

    def __init__(self, *args, **kwargs):
        """Set initial value of current_user and current_token."""
        super().__init__(*args, **kwargs)
        self.current_user = None
        self.current_token = None

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

    def _check_response(
        self,
        response,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
    ):
        if asserted_status is not None:
            msg = f"response.status_code != {asserted_status}"
            is_bad_request = response.status_code == status.HTTP_400_BAD_REQUEST
            expecting_bad_request = asserted_status == status.HTTP_400_BAD_REQUEST
            if not expecting_bad_request and is_bad_request:
                msg = f"{msg}\njson: {response.json()}"
            self.assertEqual(response.status_code, asserted_status, msg)
        if asserted_schema is not None:
            self.assertThat(response.json(), asserted_schema)

    def get(
        self,
        path: str,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.get and check status and/or the schema."""
        response = self.client.get(path, *args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def post(
        self,
        path: str,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.post and check status and/or the schema."""
        response = self.client.post(path, *args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def put(
        self,
        path: str,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.put and check status and/or the schema."""
        response = self.client.put(path, *args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def patch(
        self,
        path: str,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.patch and check status and/or the schema."""
        response = self.client.patch(path, *args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def delete(
        self,
        path: str,
        *args,
        asserted_status: int = None,
        asserted_schema: Dict[str, Any] = None,
        **kwargs,
    ):
        """Wrap self.client.delete and check status and/or the schema."""
        response = self.client.delete(path, *args, **kwargs)
        self._check_response(response, asserted_status, asserted_schema)
        return response

    def assertThat(
        self, actual: Any, matcher: BaseMatcher, reason: str = ""
    ):  # pylint: disable=invalid-name,no-self-use
        """Alias hamcrest's assert_that."""
        assert_that(actual, matcher, reason)


class JsonApiTestCase(BaseTestCase):
    """Add shortcuts for authentication tasks."""

    # We provide a default here to work around an issue
    # preventing pylint from resolving defaultless
    # instance variables on subclasses.
    # https://github.com/PyCQA/pylint/issues/3167
    schema: Type[JsonApiSchema] = None  # type: ignore

    def __init__(self, *args, **kwargs):
        """Set initial value of current_user and current_token."""
        super().__init__(*args, **kwargs)
        if getattr(self, "schema", None) is None:
            raise ImproperlyConfigured(
                "`schema` must be overridden in"
                " JsonApiTestCase subclass:"
                f"`{self.__class__.__module__}.{self.__class__.__name__}`"
                "\n\ne.g.:"
                f"\n\nclass {self.__class__.__name__}(JsonApiTestCase):"
                "\n\n    schema = JsonApiSchemaSubClass"
            )

    @property
    def resource_name(self):
        """Return the schema's resource_name."""
        return self.schema.resource_name

    def assertHasError(
        self, json: Dict[str, Any], field_name: str, error_msg: str
    ):  # pylint: disable=invalid-name
        """Assert that the error message is in the json."""
        if "errors" not in json:
            msg = f"json does not contain 'errors'.\njson: {json}"
            raise self.failureException(msg)
        for error in json["errors"]:
            if "source" in error:
                if error["source"]["pointer"].rsplit("/", 1)[-1] != field_name:
                    continue
            elif error.get("status", "") != "404":
                msg = f"non-404 error does not contain 'source'.\nerror: {error}"
                raise self.failureException(msg)
            elif field_name != "":
                msg = f"404 errors do not contain 'source'.\nerror: {error}"
                raise self.failureException(msg)
            if error["detail"] == error_msg:
                return
        msg = (
            f"json does not contain the error: '{error_msg}'"
            f" for the field '{field_name}'.\njson: {json}"
        )
        raise self.failureException(msg)
