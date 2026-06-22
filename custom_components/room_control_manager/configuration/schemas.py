"""Voluptuous schemas used by config and options flows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.helpers.selector import BooleanSelector, BooleanSelectorConfig

from ..const import *  # noqa: F403
from .selectors import area_selector, choice_selector, entity_selector, numeric_selector, room_name_selector


def _suggested(value: Any) -> dict[str, Any]:
    return {"suggested_value": value}


def room_schema(current: Mapping[str, Any]) -> vol.Schema:
    schema: dict[Any, Any] = {
        vol.Required(CONF_ROOM_NAME, description=_suggested(current.get(CONF_ROOM_NAME, ""))): room_name_selector(),
        vol.Optional(CONF_AREA_ID, description=_suggested(current.get(CONF_AREA_ID))): area_selector(),
    }
    return vol.Schema(schema)


def sensors_schema(current: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_DOOR_SENSOR, description=_suggested(current.get(CONF_DOOR_SENSOR))): entity_selector(
                ["binary_sensor"], device_classes=["door", "opening"]
            ),
            vol.Optional(CONF_PRESENCE_SENSORS, default=current.get(CONF_PRESENCE_SENSORS, [])): entity_selector(
                ["binary_sensor"], device_classes=["occupancy", "presence"], multiple=True
            ),
            vol.Optional(CONF_MOTION_SENSORS, default=current.get(CONF_MOTION_SENSORS, [])): entity_selector(
                ["binary_sensor"], device_classes=["motion"], multiple=True
            ),
            vol.Optional(CONF_TEMPERATURE_SENSORS, default=current.get(CONF_TEMPERATURE_SENSORS, [])): entity_selector(
                ["sensor"], device_classes=["temperature"], multiple=True
            ),
            vol.Optional(CONF_ILLUMINANCE_SENSORS, default=current.get(CONF_ILLUMINANCE_SENSORS, [])): entity_selector(
                ["sensor"], device_classes=["illuminance"], multiple=True
            ),
        }
    )


def actuators_schema(current: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_LIGHT_ENTITY, description=_suggested(current.get(CONF_LIGHT_ENTITY))): entity_selector(
                ["light", "switch"]
            ),
            vol.Optional(CONF_FAN_ENTITY, description=_suggested(current.get(CONF_FAN_ENTITY))): entity_selector(
                ["fan", "switch"]
            ),
            vol.Required(
                CONF_AC_CONTROL_TYPE,
                default=current.get(CONF_AC_CONTROL_TYPE, ACControlType.NONE),
            ): choice_selector([item.value for item in ACControlType], translation_key=CONF_AC_CONTROL_TYPE),
        }
    )


def climate_schema(current: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_CLIMATE_ENTITY, description=_suggested(current.get(CONF_CLIMATE_ENTITY))
            ): entity_selector(["climate"])
        }
    )


def ir_schema(current: Mapping[str, Any]) -> vol.Schema:
    def script_selector():
        return entity_selector(["script"])

    return vol.Schema(
        {
            vol.Required(CONF_IR_POWER_ON, description=_suggested(current.get(CONF_IR_POWER_ON))): script_selector(),
            vol.Required(CONF_IR_POWER_OFF, description=_suggested(current.get(CONF_IR_POWER_OFF))): script_selector(),
            vol.Optional(CONF_IR_MODE_COOL, description=_suggested(current.get(CONF_IR_MODE_COOL))): script_selector(),
            vol.Required(
                CONF_IR_TEMPERATURE_CONTROL,
                default=current.get(CONF_IR_TEMPERATURE_CONTROL, IRTemperatureControl.NONE),
            ): choice_selector(
                [item.value for item in IRTemperatureControl], translation_key=CONF_IR_TEMPERATURE_CONTROL
            ),
            vol.Optional(
                CONF_IR_TEMPERATURE_SCRIPT,
                description=_suggested(current.get(CONF_IR_TEMPERATURE_SCRIPT)),
            ): script_selector(),
            vol.Optional(
                CONF_IR_TEMPERATURE_FIELD,
                description=_suggested(current.get(CONF_IR_TEMPERATURE_FIELD, "temperature")),
            ): room_name_selector(),
            vol.Optional(CONF_IR_TEMP_UP, description=_suggested(current.get(CONF_IR_TEMP_UP))): script_selector(),
            vol.Optional(CONF_IR_TEMP_DOWN, description=_suggested(current.get(CONF_IR_TEMP_DOWN))): script_selector(),
            vol.Optional(CONF_IR_FAN_AUTO, description=_suggested(current.get(CONF_IR_FAN_AUTO))): script_selector(),
            vol.Optional(CONF_IR_FAN_LOW, description=_suggested(current.get(CONF_IR_FAN_LOW))): script_selector(),
            vol.Optional(
                CONF_IR_FAN_MEDIUM, description=_suggested(current.get(CONF_IR_FAN_MEDIUM))
            ): script_selector(),
            vol.Optional(CONF_IR_FAN_HIGH, description=_suggested(current.get(CONF_IR_FAN_HIGH))): script_selector(),
        }
    )


def review_schema() -> vol.Schema:
    return vol.Schema({vol.Required(CONF_CONFIRM, default=False): BooleanSelector(BooleanSelectorConfig())})


def modules_options_schema(current: Mapping[str, Any]) -> vol.Schema:
    boolean = BooleanSelector(BooleanSelectorConfig())
    return vol.Schema(
        {
            vol.Required(CONF_ENABLE_PRESENCE, default=current[CONF_ENABLE_PRESENCE]): boolean,
            vol.Required(CONF_ENABLE_DOOR, default=current[CONF_ENABLE_DOOR]): boolean,
            vol.Required(CONF_ENABLE_LIGHTING, default=current[CONF_ENABLE_LIGHTING]): boolean,
            vol.Required(CONF_ENABLE_FAN, default=current[CONF_ENABLE_FAN]): boolean,
            vol.Required(CONF_ENABLE_CLIMATE, default=current[CONF_ENABLE_CLIMATE]): boolean,
        }
    )


def binary_options_schema(current: Mapping[str, Any], data: Mapping[str, Any]) -> vol.Schema:
    schema: dict[Any, Any] = {
        vol.Required(CONF_PRESENCE_MODE, default=current[CONF_PRESENCE_MODE]): choice_selector(
            [item.value for item in BinaryCombineMode], translation_key=CONF_PRESENCE_MODE
        ),
        vol.Required(CONF_MOTION_MODE, default=current[CONF_MOTION_MODE]): choice_selector(
            [item.value for item in BinaryCombineMode], translation_key=CONF_MOTION_MODE
        ),
        vol.Required(CONF_NO_OCCUPANCY_DELAY, default=current[CONF_NO_OCCUPANCY_DELAY]): numeric_selector(0, 86400, 1),
    }
    presence = list(data.get(CONF_PRESENCE_SENSORS, []))
    motion = list(data.get(CONF_MOTION_SENSORS, []))
    if presence:
        schema[vol.Optional(CONF_PRESENCE_PRIMARY, description=_suggested(current.get(CONF_PRESENCE_PRIMARY)))] = (
            entity_selector(["binary_sensor"], include_entities=presence)
        )
    if motion:
        schema[vol.Optional(CONF_MOTION_PRIMARY, description=_suggested(current.get(CONF_MOTION_PRIMARY)))] = (
            entity_selector(["binary_sensor"], include_entities=motion)
        )
    return vol.Schema(schema)


def numeric_options_schema(current: Mapping[str, Any], data: Mapping[str, Any]) -> vol.Schema:
    schema: dict[Any, Any] = {
        vol.Required(CONF_TEMPERATURE_MODE, default=current[CONF_TEMPERATURE_MODE]): choice_selector(
            [item.value for item in NumericCombineMode], translation_key=CONF_TEMPERATURE_MODE
        ),
        vol.Required(CONF_ILLUMINANCE_MODE, default=current[CONF_ILLUMINANCE_MODE]): choice_selector(
            [item.value for item in NumericCombineMode], translation_key=CONF_ILLUMINANCE_MODE
        ),
    }
    temperatures = list(data.get(CONF_TEMPERATURE_SENSORS, []))
    illuminance = list(data.get(CONF_ILLUMINANCE_SENSORS, []))
    if temperatures:
        schema[
            vol.Optional(CONF_TEMPERATURE_PRIMARY, description=_suggested(current.get(CONF_TEMPERATURE_PRIMARY)))
        ] = entity_selector(["sensor"], include_entities=temperatures)
    if illuminance:
        schema[
            vol.Optional(CONF_ILLUMINANCE_PRIMARY, description=_suggested(current.get(CONF_ILLUMINANCE_PRIMARY)))
        ] = entity_selector(["sensor"], include_entities=illuminance)
    return vol.Schema(schema)


def thresholds_options_schema(current: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_LIGHT_ON_LUX, default=current[CONF_LIGHT_ON_LUX]): numeric_selector(0, 200000, 1),
            vol.Required(CONF_LIGHT_OFF_LUX, default=current[CONF_LIGHT_OFF_LUX]): numeric_selector(0, 200000, 1),
            vol.Required(CONF_FAN_ON_TEMP, default=current[CONF_FAN_ON_TEMP]): numeric_selector(-20, 80, 0.1),
            vol.Required(CONF_FAN_OFF_TEMP, default=current[CONF_FAN_OFF_TEMP]): numeric_selector(-20, 80, 0.1),
            vol.Required(CONF_CLIMATE_ON_TEMP, default=current[CONF_CLIMATE_ON_TEMP]): numeric_selector(-20, 80, 0.1),
            vol.Required(CONF_CLIMATE_OFF_TEMP, default=current[CONF_CLIMATE_OFF_TEMP]): numeric_selector(-20, 80, 0.1),
            vol.Required(CONF_DOOR_OPEN_DELAY, default=current[CONF_DOOR_OPEN_DELAY]): numeric_selector(0, 86400, 1),
            vol.Required(CONF_STARTUP_HOLD, default=current[CONF_STARTUP_HOLD]): numeric_selector(0, 3600, 1),
        }
    )


def options_review_schema() -> vol.Schema:
    return review_schema()
