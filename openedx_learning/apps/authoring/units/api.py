"""Units API.

This module provides functions to manage units.
"""

from django.db.transaction import atomic
from ..publishing import api as publishing_api
from ..containers import api as container_api
from .models import Unit, UnitVersion

from datetime import datetime

__all__ = [
    "create_unit",
    "create_unit_version",
    "create_next_unit_version",
    "create_unit_and_version",
    "get_unit",
    "get_unit_version",
    "get_latest_unit_version",
    "get_unit_version_by_version_num",
    "get_user_defined_components_in_unit_version",
    "get_initial_components_in_unit_version",
    "get_frozen_components_in_unit_version",
]


def create_unit(
    learning_package_id: int, key: str, created: datetime, created_by: int | None
) -> Unit:
    """Create a new unit.

    Args:
        learning_package_id: The learning package ID.
        key: The key.
        created: The creation date.
        created_by: The user who created the unit.
    """
    with atomic():
        container = container_api.create_container(
            learning_package_id, key, created, created_by
        )
        unit = Unit.objects.create(
            container_entity=container,
            publishable_entity=container.publishable_entity,
        )
    return unit


def create_unit_version(
    unit: Unit,
    version_num: int,
    title: str,
    publishable_entities_pk: list[int],
    created: datetime,
    created_by: int | None,
) -> Unit:
    """Create a new unit version.

    Args:
        unit_pk: The unit ID.
        version_num: The version number.
        title: The title.
        publishable_entities_pk: The publishable entities.
        entity: The entity.
        created: The creation date.
        created_by: The user who created the unit.
    """
    with atomic():
        container_entity_version = container_api.create_container_version(
            unit.container_entity.pk,
            version_num,
            title,
            publishable_entities_pk,
            unit.container_entity.publishable_entity,
            created,
            created_by,
        )
        unit_version = UnitVersion.objects.create(
            unit=unit,
            container_entity_version=container_entity_version,
            publishable_entity_version=container_entity_version.publishable_entity_version,
        )
    return unit_version


def create_next_unit_version(
    unit: Unit,
    title: str,
    publishable_entities_pk: list[int],
    created: datetime,
    created_by: int | None,
) -> Unit:
    """Create the next unit version.

    Args:
        unit_pk: The unit ID.
        title: The title.
        publishable_entities_pk: The components.
        entity: The entity.
        created: The creation date.
        created_by: The user who created the unit.
    """
    with atomic():
        # TODO: how can we enforce that publishable entities must be components?
        # This currently allows for any publishable entity to be added to a unit.
        container_entity_version = container_api.create_next_container_version(
            unit.container_entity.pk,
            title,
            publishable_entities_pk,
            unit.container_entity.publishable_entity,
            created,
            created_by,
        )
        unit_version = UnitVersion.objects.create(
            unit=unit,
            container_entity_version=container_entity_version,
            publishable_entity_version=container_entity_version.publishable_entity_version,
        )
    return unit_version


def create_unit_and_version(
    learning_package_id: int,
    key: str,
    created: datetime,
    created_by: int | None,
    title: str,
) -> tuple[Unit, UnitVersion]:
    """Create a new unit and version.

    Args:
        learning_package_id: The learning package ID.
        key: The key.
        created: The creation date.
        created_by: The user who created the unit.
    """
    with atomic():
        unit = create_unit(learning_package_id, key, created, created_by)
        unit_version = create_unit_version(
            unit,
            1,
            title,
            [],
            created,
            created_by,
        )
    return unit, unit_version


def get_unit(unit_pk: int) -> Unit:
    """Get a unit.

    Args:
        unit_pk: The unit ID.
    """
    return Unit.objects.get(pk=unit_pk)


def get_unit_version(unit_version_pk: int) -> UnitVersion:
    """Get a unit version.

    Args:
        unit_version_pk: The unit version ID.
    """
    return UnitVersion.objects.get(pk=unit_version_pk)


def get_latest_unit_version(unit_pk: int) -> UnitVersion:
    """Get the latest unit version.

    Args:
        unit_pk: The unit ID.
    """
    return Unit.objects.get(pk=unit_pk).versioning.latest


def get_unit_version_by_version_num(unit_pk: int, version_num: int) -> UnitVersion:
    """Get a unit version by version number.

    Args:
        unit_pk: The unit ID.
        version_num: The version number.
    """
    return Unit.objects.get(pk=unit_pk).versioning.get(version_num=version_num)


def get_user_defined_list_in_unit_version(unit_version_pk: int) -> list[int]:
    """Get the list in a unit version.

    Args:
        unit_version_pk: The unit version ID.
    """
    return UnitVersion.objects.get(pk=unit_version_pk).container_version.defined_list


def get_initial_list_in_unit_version(unit_version_pk: int) -> list[int]:
    """Get the initial list in a unit version.

    Args:
        unit_version_pk: The unit version ID.
    """
    return UnitVersion.objects.get(pk=unit_version_pk).container_version.initial_list


def get_frozen_list_in_unit_version(unit_version_pk: int) -> list[int]:
    """Get the frozen list in a unit version.

    Args:
        unit_version_pk: The unit version ID.
    """
    return UnitVersion.objects.get(pk=unit_version_pk).container_version.frozen_list
