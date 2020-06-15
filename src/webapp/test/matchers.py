"""Project wide hamcrest matchers."""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Union

from hamcrest import has_entries  # type: ignore
from hamcrest import (
    all_of,
    any_of,
    empty,
    equal_to,
    has_key,
    has_length,
    instance_of,
    matches_regexp,
    none,
    not_,
    not_none,
    only_contains,
)
from hamcrest.core.base_matcher import BaseMatcher  # type: ignore

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


class WrappingMatcher(BaseMatcher):
    """Matcher which wraps other Matchers."""

    def _matches(self, item):
        """Pylint expects this to be overridden."""

    @property
    def matcher(self) -> BaseMatcher:
        """Return matcher."""
        raise NotImplementedError("matcher")

    def matches(self, item, mismatch_description=None):
        """Get more descriptive mismatch description."""
        matcher = self.matcher
        match_result = matcher.matches(item)
        if not match_result and mismatch_description:
            matcher.describe_mismatch(item, mismatch_description)
        return match_result

    def describe_mismatch(self, item, mismatch_description):
        """Use the matcher to describe the mismatch."""
        self.matches(item, mismatch_description)

    def describe_to(self, description):
        """Use the matcher's description."""
        description.append_description_of(self.matcher)


class IsResourceIdentifierObject(WrappingMatcher):
    """Match a JSON:API resource identifier object."""

    def __init__(self, *, resource_name: str):
        """Initialise the class."""
        self.resource_name = resource_name

    @property
    def matcher(self) -> BaseMatcher:
        """Return matcher."""
        return has_entries(id=instance_of(str), type=equal_to(self.resource_name))


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

    @property
    def matcher(self) -> BaseMatcher:
        """Return matcher."""
        entries = {}
        if self.attributes:
            entries["attributes"] = has_entries(**self.attributes)
        if self.relationships:
            entries["relationships"] = has_entries(**self.relationships)
        return all_of(has_entries(**entries), super().matcher)


class IsToOne(IsResourceIdentifierObject):
    """Match a JSON:API To-One Relationship."""

    def __init__(self, *, optional: bool, **kwargs):
        """Initialise the class."""
        super().__init__(**kwargs)
        self.optional = optional

    @property
    def matcher(self):
        """Return matcher."""
        matcher = super().matcher
        if self.optional:
            matcher = any_of(none(), matcher)
        else:
            matcher = all_of(not_none(), matcher)
        return has_entries(data=matcher)


class IsToMany(IsResourceIdentifierObject):
    """Match a JSON:API To-Many Relationship."""

    def __init__(self, *, optional: bool, **kwargs):
        """Initialise the class."""
        super().__init__(**kwargs)
        self.optional = optional

    @property
    def matcher(self):
        """Return matcher."""
        matcher = only_contains(super().matcher)
        if self.optional:
            matcher = any_of(empty(), matcher)
        return has_entries(data=all_of(instance_of(list), matcher))


IsJsonApiRelationship = Union[IsToOne, IsToMany]


class IsDocument(WrappingMatcher):
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

    @property
    def matcher(self) -> BaseMatcher:
        """Return matcher."""
        matcher = self.resource_matcher
        if self.many:
            matcher = all_of(instance_of(list), only_contains(matcher))
            if self.optional:
                matcher = any_of(empty(), matcher)
        elif self.optional:
            matcher = any_of(none(), matcher)
        else:
            matcher = all_of(not_none(), matcher)
        include_matcher = any_of(
            not_(has_key("included")),
            has_entries(
                included=any_of(empty(), only_contains(*self.included_matchers))
            ),
        )

        return all_of(has_entries(data=matcher), include_matcher)


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
