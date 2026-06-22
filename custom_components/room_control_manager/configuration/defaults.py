"""Safe, device-independent defaults."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..const import (
    CONF_AC_CONTROL_TYPE,
    CONF_CLIMATE_OFF_TEMP,
    CONF_CLIMATE_ON_TEMP,
    CONF_DOOR_OPEN_DELAY,
    CONF_DOOR_SENSOR,
    CONF_DRY_RUN,
    CONF_ENABLE_CLIMATE,
    CONF_ENABLE_DOOR,
    CONF_ENABLE_FAN,
    CONF_ENABLE_LIGHTING,
    CONF_ENABLE_PRESENCE,
    CONF_FAN_ENTITY,
    CONF_FAN_OFF_TEMP,
    CONF_FAN_ON_TEMP,
    CONF_ILLUMINANCE_MODE,
    CONF_LIGHT_ENTITY,
    CONF_LIGHT_OFF_LUX,
    CONF_LIGHT_ON_LUX,
    CONF_MOTION_MODE,
    CONF_MOTION_SENSORS,
    CONF_NO_OCCUPANCY_DELAY,
    CONF_PRESENCE_MODE,
    CONF_PRESENCE_SENSORS,
    CONF_STARTUP_HOLD,
    CONF_TEMPERATURE_MODE,
    ACControlType,
    BinaryCombineMode,
    NumericCombineMode,
)

DEFAULT_OPTIONS: dict[str, Any] = {
    CONF_DRY_RUN: True,
    CONF_ENABLE_PRESENCE: True,
    CONF_ENABLE_DOOR: True,
    CONF_ENABLE_LIGHTING: True,
    CONF_ENABLE_FAN: True,
    CONF_ENABLE_CLIMATE: True,
    CONF_PRESENCE_MODE: BinaryCombineMode.OR,
    CONF_MOTION_MODE: BinaryCombineMode.OR,
    CONF_TEMPERATURE_MODE: NumericCombineMode.AVERAGE,
    CONF_ILLUMINANCE_MODE: NumericCombineMode.AVERAGE,
    CONF_LIGHT_ON_LUX: 50.0,
    CONF_LIGHT_OFF_LUX: 80.0,
    CONF_FAN_ON_TEMP: 28.0,
    CONF_FAN_OFF_TEMP: 27.0,
    CONF_CLIMATE_ON_TEMP: 30.0,
    CONF_CLIMATE_OFF_TEMP: 27.0,
    CONF_NO_OCCUPANCY_DELAY: 180,
    CONF_DOOR_OPEN_DELAY: 180,
    CONF_STARTUP_HOLD: 60,
}


def build_default_options(data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return safe defaults, enabling only modules configured for this room."""

    options = dict(DEFAULT_OPTIONS)
    if data is None:
        return options
    options[CONF_ENABLE_PRESENCE] = bool(data.get(CONF_PRESENCE_SENSORS) or data.get(CONF_MOTION_SENSORS))
    options[CONF_ENABLE_DOOR] = bool(data.get(CONF_DOOR_SENSOR))
    options[CONF_ENABLE_LIGHTING] = bool(data.get(CONF_LIGHT_ENTITY))
    options[CONF_ENABLE_FAN] = bool(data.get(CONF_FAN_ENTITY))
    options[CONF_ENABLE_CLIMATE] = data.get(CONF_AC_CONTROL_TYPE, ACControlType.NONE) != ACControlType.NONE
    return options
