"""Validation for config-entry data and options."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.core import split_entity_id

from ..const import *  # noqa: F403
from ..models import ValidationResult
from .normalization import normalize_entity_list

ROLE_DOMAINS: dict[str, set[str]] = {
    CONF_DOOR_SENSOR: {"binary_sensor"},
    CONF_PRESENCE_SENSORS: {"binary_sensor"},
    CONF_MOTION_SENSORS: {"binary_sensor"},
    CONF_TEMPERATURE_SENSORS: {"sensor"},
    CONF_ILLUMINANCE_SENSORS: {"sensor"},
    CONF_LIGHT_ENTITY: {"light", "switch"},
    CONF_FAN_ENTITY: {"fan", "switch"},
    CONF_CLIMATE_ENTITY: {"climate"},
    CONF_IR_POWER_ON: {"script"},
    CONF_IR_POWER_OFF: {"script"},
    CONF_IR_MODE_COOL: {"script"},
    CONF_IR_TEMPERATURE_SCRIPT: {"script"},
    CONF_IR_TEMP_UP: {"script"},
    CONF_IR_TEMP_DOWN: {"script"},
    CONF_IR_FAN_AUTO: {"script"},
    CONF_IR_FAN_LOW: {"script"},
    CONF_IR_FAN_MEDIUM: {"script"},
    CONF_IR_FAN_HIGH: {"script"},
}


def _entity_exists(hass: Any, entity_id: str) -> bool:
    registry = hass.helpers.entity_registry.async_get(hass) if hasattr(hass, "helpers") else None
    if registry is not None and registry.async_get(entity_id) is not None:
        return True
    return hass.states.get(entity_id) is not None


def validate_installation_data(hass: Any, data: Mapping[str, Any]) -> ValidationResult:
    """Validate installation data without requiring every role to be populated."""

    errors: list[str] = []
    warnings: list[str] = []
    if not str(data.get(CONF_ROOM_NAME, "")).strip():
        errors.append("room_name_required")

    for key, domains in ROLE_DOMAINS.items():
        for entity_id in normalize_entity_list(data.get(key)):
            try:
                domain, _ = split_entity_id(entity_id)
            except ValueError:
                errors.append(f"invalid_entity:{key}")
                continue
            if domain not in domains:
                errors.append(f"wrong_domain:{key}")
            if hass.states.get(entity_id) is None:
                warnings.append(f"entity_not_loaded:{key}")
            elif hass.states[entity_id].state in {"unknown", "unavailable"}:
                warnings.append(f"entity_unavailable:{key}")

    light = data.get(CONF_LIGHT_ENTITY)
    fan = data.get(CONF_FAN_ENTITY)
    if light and light == fan:
        errors.append("same_light_and_fan")

    ac_type = data.get(CONF_AC_CONTROL_TYPE, ACControlType.NONE)
    if ac_type == ACControlType.CLIMATE and not data.get(CONF_CLIMATE_ENTITY):
        errors.append("climate_required")
    if ac_type == ACControlType.IR_SCRIPTS:
        if not data.get(CONF_IR_POWER_ON) or not data.get(CONF_IR_POWER_OFF):
            errors.append("ir_power_scripts_required")
        if data.get(CONF_IR_POWER_ON) == data.get(CONF_IR_POWER_OFF):
            errors.append("ir_power_scripts_same")
        temperature_control = data.get(CONF_IR_TEMPERATURE_CONTROL, IRTemperatureControl.NONE)
        if temperature_control == IRTemperatureControl.DIRECT_SCRIPT and not data.get(CONF_IR_TEMPERATURE_SCRIPT):
            errors.append("ir_direct_script_required")
        if temperature_control == IRTemperatureControl.UP_DOWN and (
            not data.get(CONF_IR_TEMP_UP) or not data.get(CONF_IR_TEMP_DOWN)
        ):
            errors.append("ir_up_down_required")

    if not data.get(CONF_PRESENCE_SENSORS) and not data.get(CONF_MOTION_SENSORS):
        warnings.append("no_occupancy_sensor")
    if data.get(CONF_LIGHT_ENTITY) and not data.get(CONF_ILLUMINANCE_SENSORS):
        warnings.append("lighting_without_illuminance")
    if (data.get(CONF_FAN_ENTITY) or ac_type != ACControlType.NONE) and not data.get(CONF_TEMPERATURE_SENSORS):
        warnings.append("temperature_control_without_sensor")
    return ValidationResult(tuple(sorted(set(errors))), tuple(sorted(set(warnings))))


def validate_options(data: Mapping[str, Any], options: Mapping[str, Any]) -> ValidationResult:
    """Validate behavioral options and primary sensor selections."""

    errors: list[str] = []
    warnings: list[str] = []
    if options.get(CONF_DRY_RUN) is not True:
        errors.append("dry_run_required")
    if float(options[CONF_LIGHT_ON_LUX]) >= float(options[CONF_LIGHT_OFF_LUX]):
        errors.append("light_hysteresis_invalid")
    if float(options[CONF_FAN_ON_TEMP]) <= float(options[CONF_FAN_OFF_TEMP]):
        errors.append("fan_hysteresis_invalid")
    if float(options[CONF_CLIMATE_ON_TEMP]) <= float(options[CONF_CLIMATE_OFF_TEMP]):
        errors.append("climate_hysteresis_invalid")

    primary_checks = (
        (CONF_PRESENCE_MODE, CONF_PRESENCE_PRIMARY, CONF_PRESENCE_SENSORS),
        (CONF_MOTION_MODE, CONF_MOTION_PRIMARY, CONF_MOTION_SENSORS),
        (CONF_TEMPERATURE_MODE, CONF_TEMPERATURE_PRIMARY, CONF_TEMPERATURE_SENSORS),
        (CONF_ILLUMINANCE_MODE, CONF_ILLUMINANCE_PRIMARY, CONF_ILLUMINANCE_SENSORS),
    )
    for mode_key, primary_key, list_key in primary_checks:
        if options.get(mode_key) != "primary":
            continue
        selected = normalize_entity_list(data.get(list_key))
        primary = options.get(primary_key)
        if selected and primary not in selected:
            errors.append(f"primary_not_selected:{primary_key}")
        elif not selected:
            warnings.append(f"primary_without_sensors:{primary_key}")

    for key in (CONF_NO_OCCUPANCY_DELAY, CONF_DOOR_OPEN_DELAY, CONF_STARTUP_HOLD):
        if float(options.get(key, 0)) < 0:
            errors.append(f"negative_delay:{key}")
    return ValidationResult(tuple(sorted(set(errors))), tuple(sorted(set(warnings))))
