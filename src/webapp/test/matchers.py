"""Project wide hamcrest matchers."""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Union

from hamcrest import has_entries  # type: ignore
from hamcrest import (
    all_of,
    any_of,
    has_length,
    instance_of,
    matches_regexp,
    only_contains,
)
from hamcrest.core.base_matcher import BaseMatcher  # type: ignore
from hamcrest.core.string_description import StringDescription

ISODATE_REGEX = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?.*"
UUID_REGEX = r"-?".join(
    [
        r"[a-f0-9]{8}",
        r"[a-f0-9]{4}",
        r"4[a-f0-9]{3}",
        r"[89ab][a-f0-9]{3}",
        r"[a-f0-9]{12}",
    ]
)


def is_regex(regex: str, nullable=False) -> Callable[[Optional[str]], bool]:
    """Return a function to check whether an Optional[str] matches a regex."""
    good = all_of(instance_of(str), matches_regexp(r"^%s$" % regex))
    return any_of(good, None) if nullable else good


def is_date(nullable: bool = False) -> Callable[[Optional[str]], bool]:
    """Return a function to check whether the string is ISO8601 formatted."""
    return is_regex(ISODATE_REGEX, nullable)


def is_uuid(nullable: bool = False) -> Callable[[Optional[str]], bool]:
    """Return a function to check whether the string is a UUID."""
    return is_regex(UUID_REGEX, nullable)


class IsResourceIdentifierObject(BaseMatcher):
    """Match a JSON:API resource identifier object."""

    def __init__(self, *, resource_name: str):
        """Initialise the class."""
        self.resource_name = resource_name

    def _matches(self, item):
        """Pylint expects this to be overridden."""

    def matches(self, item, mismatch_description=None):
        """Return whether the item is a resource identifier."""
        if mismatch_description is None:
            mismatch_description = StringDescription()
        if not isinstance(item, dict):
            mismatch_description.append(
                f"not a `dict`\n     got: `{item.__class__.__name__}`"
            )
            return False
        if "id" not in item:
            mismatch_description.append("missing key id")
            return False
        id_value = item["id"]
        if not isinstance(id_value, str):
            mismatch_description.append("id is not a string")
            return False
        if id_value == "":
            mismatch_description.append("id is blank")
            return False
        if "type" not in item:
            mismatch_description.append("missing key type")
            return False
        type_value = item["type"]
        if type_value != self.resource_name:
            mismatch_description.append(f'type does not match "{self.resource_name}"')
            return False
        return True

    def describe_mismatch(self, item, mismatch_description):
        """Use the matcher to describe the mismatch."""
        self.matches(item, mismatch_description)

    def describe_to(self, description):
        """Describe the instance."""
        description.append(f'resource object "{self.resource_name}"')


class IsResourceObject(IsResourceIdentifierObject):
    """Match a JSON:API resource identifier object."""

    def __init__(
        self,
        *,
        attributes: Dict[str, BaseMatcher],
        relationships: Dict[str, IsJsonApiRelationship],
        **kwargs,
    ):
        """Initialise the class."""
        super().__init__(**kwargs)
        self.attributes = attributes
        self.relationships = relationships

    def matches(self, item, mismatch_description=None):
        """Return whether the item is a resource object."""
        if mismatch_description is None:
            mismatch_description = StringDescription()
        match_result = super().matches(item, mismatch_description)
        if not match_result:
            return match_result
        if not self._match_dict(
            item,
            mismatch_description,
            attr_name="attributes",
            attr_description="attribute",
            matcher_dict=self.attributes,
        ):
            return False
        if not self._match_dict(
            item,
            mismatch_description,
            attr_name="relationships",
            attr_description="relationship",
            matcher_dict=self.relationships,
        ):
            return False
        return True

    def describe_to(self, description):
        """Describe the instance."""
        super().describe_to(description)
        if self.attributes:
            description.append(" with attributes: ")
            self._describe_dict(self.attributes, description)
        else:
            description.append(" with no attributes")
        if self.relationships:
            description.append(" with relationships: ")
            self._describe_dict(self.relationships, description)
        else:
            description.append(" with no relationships")

    def _match_dict(  # pylint: disable=no-self-use,too-many-arguments
        self, item, mismatch_description, attr_name, attr_description, matcher_dict
    ):
        """Ensure the given attr is present and matches the matcher_dict."""
        if not matcher_dict:
            # nothing to match - return early
            return True
        if not attr_name in item:
            mismatch_description.append(f' missing key "{attr_name}" ')
            return False
        dict_maybe = item[attr_name]
        if not isinstance(dict_maybe, dict):
            mismatch_description.append(
                f'"{attr_name}" value is not a `dict`\n    '
                f"got: `{dict_maybe.__class__.__name__}`"
            )
            return False
        for key, matcher in matcher_dict.items():
            if key not in dict_maybe:
                mismatch_description.append(
                    f'the {attr_description} "{key}" is missing '
                )
                return False
            value = dict_maybe[key]
            match_result = matcher.matches(value)
            if not match_result:
                mismatch_description.append(
                    f'the {attr_description} "{key}" did not match "'
                )
                mismatch_description.append_description_of(matcher)
                mismatch_description.append('" ')
                matcher.describe_mismatch(value, mismatch_description)
                return match_result
        return True

    def _describe_dict(self, attrs, description):  # pylint: disable=no-self-use
        """Describe the dict."""
        description.append("<{")
        first = True
        for key, matcher in attrs.items():
            if not first:
                description.append(",")
                first = False
            description.append(f'"{key}": ')
            description.append_description_of(matcher)
        description.append("}>")


class IsToOne(IsResourceIdentifierObject):
    """Match a JSON:API To-One Relationship."""

    def __init__(self, *, optional: bool, **kwargs):
        """Initialise the class."""
        super().__init__(**kwargs)
        self.optional = optional

    def matches(self, item, mismatch_description=None):
        """Return whether the item is a valid to-one relationship."""
        if mismatch_description is None:
            mismatch_description = StringDescription()
        if "data" not in item:
            mismatch_description.append('missing key "data"')
            return False
        if not self.optional and not item["data"]:
            mismatch_description.append("non-optional to-one relationship is ")
            mismatch_description.append_description_of(item["data"])
            return False
        return super().matches(item["data"], mismatch_description)

    def describe_to(self, description):
        """Describe the instance."""
        description.append(f'has one "{self.resource_name}"')


class IsToMany(IsResourceIdentifierObject):
    """Match a JSON:API To-Many Relationship."""

    def __init__(self, *, optional: bool, **kwargs):
        """Initialise the class."""
        super().__init__(**kwargs)
        self.optional = optional

    def matches(self, item, mismatch_description=None):
        """Return whether the item is a valid to-many relationship."""
        if mismatch_description is None:
            mismatch_description = StringDescription()
        if "data" not in item:
            mismatch_description.append('missing key "data"')
            return False
        if not isinstance(item["data"], list):
            mismatch_description.append(
                "to-many relationship is not a `list`\n     "
                f"got: `{item.__class__.__name__}`"
            )
            return False
        if not self.optional and not item["data"]:
            mismatch_description.append("non-optional to-many relationship is ")
            mismatch_description.append_description_of(item["data"])
            return False
        for index, data in enumerate(item["data"]):
            if not super().matches(data):
                mismatch_description.append(
                    f"to-many relationship at index {index}"
                    " does not match. Failed because: "
                )
                super().matches(data, mismatch_description)
                return False
        return True

    def describe_to(self, description):
        """Describe the instance."""
        description.append(f'has many "{self.resource_name}"')


IsJsonApiRelationship = Union[IsToOne, IsToMany]


class IsDocument(BaseMatcher):
    """Match a JSON:API top level document."""

    def __init__(
        self,
        *,
        resource_matcher: IsResourceIdentifierObject,
        included_matchers: List[IsResourceObject],
        optional: bool,
        many: bool,
    ):
        """Initialise the class."""
        super().__init__()
        self.resource_matcher = resource_matcher
        self.included_matchers = included_matchers
        self.optional = optional
        self.many = many

    def _matches(self, item):
        """Pylint expects this to be overridden."""

    def matches(self, item, mismatch_description=None):
        """Return whether the item is a json:api document."""
        if mismatch_description is None:
            mismatch_description = StringDescription()
        if "data" not in item:
            mismatch_description.append('missing key "data"')
            return False
        if not self.optional and not item["data"]:
            mismatch_description.append('non-optional "data" is ')
            mismatch_description.append_description_of(item["data"])
            return False
        if self.many:
            if not isinstance(item["data"], list):
                mismatch_description.append(
                    f'"data" is not a `list`\n     got: `{item.__class__.__name__}`'
                )
                return False
            for index, data in enumerate(item["data"]):
                if not self._match_resource(data, mismatch_description, index=index):
                    return False
        elif not self._match_resource(item["data"], mismatch_description):
            return False
        return self._matches_includes(item, mismatch_description)

    def _match_resource(self, item, mismatch_description, index=None):
        """Check whether the resource matches the resource matcher."""
        if not self.resource_matcher.matches(item):
            if index is not None:
                mismatch_description.append(
                    f"data item at index {index} does not match. Failed because: "
                )
            else:
                mismatch_description.append("data does not match. Failed because: ")
            self.resource_matcher.describe_mismatch(item, mismatch_description)
            append_item(item, mismatch_description)
            return False
        return True

    def _matches_includes(self, item, mismatch_description):
        """Check the includes are valid."""
        if "included" in item:
            if not isinstance(item["included"], list):
                mismatch_description.append(
                    f'"included" is not a `list`\n     got: `{item.__class__.__name__}`'
                )
                return False
            include_matcher = any_of(self.included_matchers)
            for index, include in enumerate(item["included"]):
                if not include_matcher.matches(include):
                    mismatch_description.append(
                        f"include at index {index} does not match. Failed because: "
                    )
                    include_matcher.describe_mismatch(include, self.included_matchers)
                    append_item(include, mismatch_description)
                    return False
        return True

    def describe_mismatch(self, item, mismatch_description):
        """Use the matcher to describe the mismatch."""
        self.matches(item, mismatch_description)

    def describe_to(self, description):
        """Describe the instance."""
        optional = "optional" if self.optional else "non-optional"
        cardinality = "many" if self.many else "one"
        description.append(f"a json:api document containing {cardinality} {optional} ")
        description.append_description_of(self.resource_matcher)


def append_item(item, mismatch_description):
    """Append the item if the mismatch_description is not None."""
    if mismatch_description:
        mismatch_description.append("\n     item: ")
        mismatch_description.append_description_of(item)


def is_geo_point():
    """Return matcher for geo point."""
    return all_of(has_length(2), only_contains(instance_of(float)))


def is_geo_lring():
    """Return matcher for geo lring."""
    return only_contains(is_geo_point())


def is_geo_poly():
    """Return matcher for geo poly."""
    return only_contains(is_geo_lring())


def is_geo_multi():
    """Return matcher for geo multi."""
    return only_contains(is_geo_poly())


def is_multipoly():
    """Return matcher for MultiPolygon."""
    return has_entries({"type": "MultiPolygon", "coordinates": is_geo_multi()})


def is_feature(props: dict) -> BaseMatcher:
    """Return matcher for Feature with given feature & properties."""
    return has_entries(
        {
            "type": "Feature",
            "geometry": any_of(None, is_multipoly()),
            "properties": has_entries(props),
        }
    )


def is_featurecollection(props: dict) -> BaseMatcher:
    """Get matcher for collection with given feature & properties."""
    return has_entries(
        {"type": "FeatureCollection", "features": only_contains(is_feature(props))}
    )


def is_to_one(*, resource_name: str, optional=False):
    """Return an instance of IsToOne."""
    return IsToOne(resource_name=resource_name, optional=optional)


def is_to_many(*, resource_name: str, optional=False):
    """Return an instance of IsToOne."""
    return IsToMany(resource_name=resource_name, optional=optional)
