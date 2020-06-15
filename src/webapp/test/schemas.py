"""Base schema definition."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from hamcrest import any_of, empty, has_entries, only_contains
from hamcrest.core.matcher import Matcher

from webapp.test.matchers import (
    IsDocument,
    IsJsonApiRelationship,
    IsResourceObject,
    IsToMany,
    IsToOne,
)


class ApiSchema:
    """Schema class intended for use with rest_framework's APITestCase."""

    fields: Dict[str, Any]

    @classmethod
    def get_matcher(
        cls,
        *,
        exclude: List[str] = None,
        many: Optional[bool] = False,
        optional: Optional[bool] = False,
    ):
        """Return a matcher which matches a standard drf response.

        Any fields specified in `exclude` will not be added to the matcher.
        """
        exclude = exclude or []
        matcher = has_entries(
            **{k: v for k, v in cls.fields.items() if k not in exclude}
        )
        if many:
            matcher = only_contains(matcher)
            if optional:
                matcher = any_of(empty(), matcher)
            matcher = has_entries(results=matcher)
        return matcher


class SchemaBase(type):
    """Ensure JsonApiSchema subclasses are properly configured."""

    def __new__(cls, *args, **kwargs):
        """Ensure JsonApiSchema subclasses are properly configured."""
        schema = super().__new__(cls, *args, **kwargs)
        if schema.__name__ == "JsonApiSchema" and schema.__module__ == cls.__module__:
            return schema
        required_attributes = [
            "resource_name",
            "includes",
            "attributes",
            "relationships",
        ]
        missing_attributes = ", ".join(
            [
                f"`{attr}`"
                for attr in required_attributes
                if getattr(schema, attr, None) is None
            ]
        )
        if missing_attributes:
            raise ImproperlyConfigured(
                f"The following attribute(s) {missing_attributes}"
                " must be overridden in Schema subclass: "
                f"`{schema.__module__}.{schema.__name__}`"
                "\n\ne.g.:"
                f"\n\nclass {schema.__name__}(JsonApiSchema):"
                '\n\n    resource_name = "resource-name"'
                "\n    attributes: Dict[str, Any] = {}"
                "\n    relationships: Dict[str, IsJsonApiRelationship] = {}"
                "\n    includes: List[Union[IsResourceObject, str]] = []"
            )
        return schema


class JsonApiSchema(metaclass=SchemaBase):
    """Schema class intended for use with JsonApiTestCase."""

    resource_name: str
    attributes: Dict[str, Any]
    relationships: Dict[str, IsJsonApiRelationship]
    # includes should be either a Matcher, a subclass of JsonApiSchema
    # or a dotted path that resolves to the either of the aforementioned
    includes: List[Union[IsResourceObject, str]]

    @classmethod
    def get_matcher(
        cls,
        *,
        exclude: List[str] = None,
        many: Optional[bool] = None,
        optional: Optional[bool] = None,
        as_document=True,
    ) -> Matcher:
        """Return a matcher which matches a valid JSON:API format.

        Any fields specified in `exclude` will not be added into the matcher.
        If `as_document` is False, then `many` and `optional` must not be
        supplied as they are simply passed on to the IsDocument matcher.
        `many` defaults to False if `as_document is True.
        `optional` defaults to True if `as_dcument` is True.
        """
        assert as_document or (not as_document and many is None and optional is None), (
            "If `as_document` is False, then `many` and `optional`"
            " must not be supplied as they are simply passed on to"
            " the IsDocument matcher."
        )
        exclude = exclude or []
        matcher = IsResourceObject(
            resource_name=cls.resource_name,
            attributes={k: v for k, v in cls.attributes.items() if k not in exclude},
            relationships={
                k: v for k, v in cls.relationships.items() if k not in exclude
            },
        )
        if as_document:
            return IsDocument(
                resource_matcher=matcher,
                included_matchers=cls.get_resolved_included_matchers(),
                optional=optional if optional is not None else False,
                many=many if many is not None else False,
            )
        return matcher

    @classmethod
    # pylint: disable=redefined-builtin,invalid-name
    def get_data(cls, id: Optional[Any] = None, **kwargs,) -> Dict[str, Any]:
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

    @classmethod
    def get_resolved_included_matchers(cls):
        """Return the resolved list of included matchers."""
        if not hasattr(cls, "_resolved_included_matchers"):
            matchers = []
            for include in cls.includes:
                exception_msg = (
                    f"The matcher `{include}` in "
                    f"`{cls.__module__}.{cls.__name__}.includes` is"
                    ' not a matcher, a class with a "get_matcher"'
                    " classmethod, or a dotted string path that resolves"
                    " to either of the aforementioned."
                )
                matcher = include
                if isinstance(include, str):
                    try:
                        matcher = import_string(matcher)
                    except ImportError:
                        raise ImproperlyConfigured(exception_msg)
                if not isinstance(matcher, Matcher):
                    if hasattr(matcher, "get_matcher"):
                        matcher = matcher.get_matcher(as_document=False)
                    else:
                        raise ImproperlyConfigured(exception_msg)
                matchers.append(matcher)
            cls._resolved_included_matchers = matchers
        return cls._resolved_included_matchers

    @classmethod
    def get_id(
        cls, resource_name: str, id: Optional[Any] = None
    ):  # pylint: disable=redefined-builtin,invalid-name
        """Return JSON:API compatible id."""
        data = {"type": resource_name}
        if id is not None:
            data["id"] = str(id)
        return data

    @classmethod
    def get_to_one(cls, name: str, instance: Any) -> Dict[str, Dict[str, str]]:
        """Return JSON:API compatible `to one`."""
        return {"data": cls.get_id(name, instance.pk) if instance else None}

    @classmethod
    def get_to_many(
        cls, name: str, instances: List[Any]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Return JSON:API compatible `to many`."""
        return {"data": [cls.get_id(name, i.pk) for i in instances if i is not None]}

    @classmethod
    def get_relationship(cls, name, instance: Union[List[Any], Any]):
        """Get relationship based on name."""
        matcher = cls.relationships[name]
        if isinstance(matcher, IsToOne):
            return cls.get_to_one(matcher.resource_name, instance)
        if isinstance(matcher, IsToMany):
            return cls.get_to_many(matcher.resource_name, instance)
        class_name = cls.__name__
        value = f'{class_name}.relationships["{name}"]'
        raise KeyError(f"Expected {value} to be a instance of IsToOne or IsToMany.")
