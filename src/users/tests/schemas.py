"""Schemas for users app."""
from typing import Dict, List, Union

from hamcrest import instance_of

from webapp.test.matchers import IsJsonApiRelationship, IsResourceObject, is_to_one
from webapp.test.schemas import JsonApiSchema


class UsersSchema(JsonApiSchema):
    """Schema for users."""

    resource_name = "users"
    attributes = {"email": instance_of(str)}
    relationships: Dict[str, IsJsonApiRelationship] = {}
    includes: List[Union[IsResourceObject, str]] = []


class SessionsSchema(JsonApiSchema):
    """Schema for sessions."""

    resource_name = "sessions"
    attributes = {"token": instance_of(str)}
    relationships = {"user": is_to_one(resource_name="users")}
    includes: List[Union[IsResourceObject, str]] = []
