"""Assess selected entity availability per module."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from ..configuration.normalization import normalize_entity_list
from ..const import *  # noqa: F403
from ..models import ModuleStatus


def _problem_for(hass: Any, entity_id: str) -> str | None:
    state = hass.states.get(entity_id)
    if state is None:
        return f"missing:{entity_id}"
    if state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
        return f"unavailable:{entity_id}"
    return None


def _problems(hass: Any, entity_ids: list[str]) -> tuple[str, ...]:
    return tuple(problem for entity_id in entity_ids if (problem := _problem_for(hass, entity_id)))


def assess_module_statuses(
    hass: Any, data: Mapping[str, Any], options: Mapping[str, Any]
) -> dict[ModuleName, ModuleStatus]:
    """Return isolated readiness status for each logical module."""

    occupancy_entities = normalize_entity_list(data.get(CONF_PRESENCE_SENSORS)) + normalize_entity_list(
        data.get(CONF_MOTION_SENSORS)
    )
    temperature_entities = normalize_entity_list(data.get(CONF_TEMPERATURE_SENSORS))
    statuses: dict[ModuleName, ModuleStatus] = {}

    presence_enabled = bool(options.get(CONF_ENABLE_PRESENCE, False))
    presence_problems = list(_problems(hass, occupancy_entities))
    if presence_enabled and not occupancy_entities:
        presence_problems.append("not_configured:occupancy")
    statuses[ModuleName.PRESENCE] = ModuleStatus(
        ModuleName.PRESENCE,
        presence_enabled,
        presence_enabled and bool(occupancy_entities) and not presence_problems,
        tuple(presence_problems),
    )

    door_enabled = bool(options.get(CONF_ENABLE_DOOR, False))
    door_entities = normalize_entity_list(data.get(CONF_DOOR_SENSOR))
    door_problems = list(_problems(hass, door_entities))
    if door_enabled and not door_entities:
        door_problems.append("not_configured:door")
    statuses[ModuleName.DOOR] = ModuleStatus(
        ModuleName.DOOR,
        door_enabled,
        door_enabled and bool(door_entities) and not door_problems,
        tuple(door_problems),
    )

    lighting_enabled = bool(options.get(CONF_ENABLE_LIGHTING, False))
    light_entities = normalize_entity_list(data.get(CONF_LIGHT_ENTITY))
    illuminance_entities = normalize_entity_list(data.get(CONF_ILLUMINANCE_SENSORS))
    lighting_required = light_entities + illuminance_entities + occupancy_entities
    lighting_problems = list(_problems(hass, lighting_required))
    if lighting_enabled and not light_entities:
        lighting_problems.append("not_configured:light")
    if lighting_enabled and not illuminance_entities:
        lighting_problems.append("not_configured:illuminance")
    if lighting_enabled and not occupancy_entities:
        lighting_problems.append("not_configured:occupancy")
    statuses[ModuleName.LIGHTING] = ModuleStatus(
        ModuleName.LIGHTING,
        lighting_enabled,
        lighting_enabled
        and bool(light_entities)
        and bool(illuminance_entities)
        and bool(occupancy_entities)
        and not lighting_problems,
        tuple(lighting_problems),
    )

    fan_enabled = bool(options.get(CONF_ENABLE_FAN, False))
    fan_entities = normalize_entity_list(data.get(CONF_FAN_ENTITY))
    fan_required = fan_entities + temperature_entities + occupancy_entities
    fan_problems = list(_problems(hass, fan_required))
    if fan_enabled and not fan_entities:
        fan_problems.append("not_configured:fan")
    if fan_enabled and not temperature_entities:
        fan_problems.append("not_configured:temperature")
    if fan_enabled and not occupancy_entities:
        fan_problems.append("not_configured:occupancy")
    statuses[ModuleName.FAN] = ModuleStatus(
        ModuleName.FAN,
        fan_enabled,
        fan_enabled
        and bool(fan_entities)
        and bool(temperature_entities)
        and bool(occupancy_entities)
        and not fan_problems,
        tuple(fan_problems),
    )

    climate_enabled = bool(options.get(CONF_ENABLE_CLIMATE, False))
    ac_type = data.get(CONF_AC_CONTROL_TYPE, ACControlType.NONE)
    climate_entities: list[str] = []
    if ac_type == ACControlType.CLIMATE:
        climate_entities = normalize_entity_list(data.get(CONF_CLIMATE_ENTITY))
    elif ac_type == ACControlType.IR_SCRIPTS:
        climate_entities = normalize_entity_list(data.get(CONF_IR_POWER_ON)) + normalize_entity_list(
            data.get(CONF_IR_POWER_OFF)
        )
    climate_required = climate_entities + temperature_entities + occupancy_entities
    climate_problems = list(_problems(hass, climate_required))
    if climate_enabled and ac_type == ACControlType.NONE:
        climate_problems.append("not_configured:climate")
    if climate_enabled and not climate_entities:
        climate_problems.append("not_configured:climate")
    if climate_enabled and not temperature_entities:
        climate_problems.append("not_configured:temperature")
    if climate_enabled and not occupancy_entities:
        climate_problems.append("not_configured:occupancy")
    statuses[ModuleName.CLIMATE] = ModuleStatus(
        ModuleName.CLIMATE,
        climate_enabled,
        climate_enabled
        and ac_type != ACControlType.NONE
        and bool(climate_entities)
        and bool(temperature_entities)
        and bool(occupancy_entities)
        and not climate_problems,
        tuple(climate_problems),
    )
    return statuses
