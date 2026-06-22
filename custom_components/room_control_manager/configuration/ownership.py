"""Cross-room ownership checks."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping
from typing import Any

from ..const import (
    CONF_CLIMATE_ENTITY,
    CONF_DOOR_SENSOR,
    CONF_FAN_ENTITY,
    CONF_ILLUMINANCE_SENSORS,
    CONF_IR_FAN_AUTO,
    CONF_IR_FAN_HIGH,
    CONF_IR_FAN_LOW,
    CONF_IR_FAN_MEDIUM,
    CONF_IR_MODE_COOL,
    CONF_IR_POWER_OFF,
    CONF_IR_POWER_ON,
    CONF_IR_TEMP_DOWN,
    CONF_IR_TEMP_UP,
    CONF_IR_TEMPERATURE_SCRIPT,
    CONF_LIGHT_ENTITY,
    CONF_MOTION_SENSORS,
    CONF_PRESENCE_SENSORS,
    CONF_TEMPERATURE_SENSORS,
    DOMAIN,
)
from ..models import OwnershipResult
from .normalization import normalize_entity_list

ACTUATOR_KEYS: tuple[str, ...] = (
    CONF_LIGHT_ENTITY,
    CONF_FAN_ENTITY,
    CONF_CLIMATE_ENTITY,
    CONF_IR_POWER_ON,
    CONF_IR_POWER_OFF,
    CONF_IR_MODE_COOL,
    CONF_IR_TEMPERATURE_SCRIPT,
    CONF_IR_TEMP_UP,
    CONF_IR_TEMP_DOWN,
    CONF_IR_FAN_AUTO,
    CONF_IR_FAN_LOW,
    CONF_IR_FAN_MEDIUM,
    CONF_IR_FAN_HIGH,
)
OWNERSHIP_LOCK_KEY = "ownership_lock"

SENSOR_KEYS: tuple[str, ...] = (
    CONF_DOOR_SENSOR,
    CONF_PRESENCE_SENSORS,
    CONF_MOTION_SENSORS,
    CONF_TEMPERATURE_SENSORS,
    CONF_ILLUMINANCE_SENSORS,
)


def _entities_for_keys(data: Mapping[str, Any], keys: Iterable[str]) -> set[str]:
    entities: set[str] = set()
    for key in keys:
        entities.update(normalize_entity_list(data.get(key)))
    return entities


def selected_actuators(data: Mapping[str, Any]) -> set[str]:
    """Return every command-capable entity selected by this room."""

    return _entities_for_keys(data, ACTUATOR_KEYS)


def selected_sensors(data: Mapping[str, Any]) -> set[str]:
    """Return every sensor selected by this room."""

    return _entities_for_keys(data, SENSOR_KEYS)


def get_ownership_lock(hass: Any) -> asyncio.Lock:
    """Return the integration-wide lock used for final ownership commits."""

    domain_data = hass.data.setdefault(DOMAIN, {})
    lock = domain_data.get(OWNERSHIP_LOCK_KEY)
    if isinstance(lock, asyncio.Lock):
        return lock
    lock = asyncio.Lock()
    domain_data[OWNERSHIP_LOCK_KEY] = lock
    return lock


def check_ownership(hass: Any, candidate: Mapping[str, Any], *, exclude_entry_id: str | None = None) -> OwnershipResult:
    """Check candidate data against every other Room Control Manager entry."""

    candidate_actuators = selected_actuators(candidate)
    candidate_sensors = selected_sensors(candidate)
    conflicts: set[str] = set()
    shared: set[str] = set()
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.entry_id == exclude_entry_id:
            continue
        conflicts.update(candidate_actuators.intersection(selected_actuators(entry.data)))
        shared.update(candidate_sensors.intersection(selected_sensors(entry.data)))
    return OwnershipResult(tuple(sorted(conflicts)), tuple(sorted(shared)))
