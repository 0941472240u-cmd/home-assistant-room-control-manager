"""Constants for Room Control Manager."""

from __future__ import annotations

from enum import StrEnum

from homeassistant.const import Platform

DOMAIN = "room_control_manager"
NAME = "Room Control Manager"
VERSION = "0.1.0"
CONFIG_ENTRY_VERSION = 1
CONFIG_ENTRY_MINOR_VERSION = 0
PLATFORMS: tuple[Platform, ...] = (Platform.SENSOR, Platform.BINARY_SENSOR)

CONF_ROOM_ID = "room_id"
CONF_ROOM_NAME = "room_name"
CONF_AREA_ID = "area_id"
CONF_DOOR_SENSOR = "door_sensor"
CONF_PRESENCE_SENSORS = "presence_sensors"
CONF_MOTION_SENSORS = "motion_sensors"
CONF_TEMPERATURE_SENSORS = "temperature_sensors"
CONF_ILLUMINANCE_SENSORS = "illuminance_sensors"
CONF_LIGHT_ENTITY = "light_entity"
CONF_FAN_ENTITY = "fan_entity"
CONF_AC_CONTROL_TYPE = "ac_control_type"
CONF_CLIMATE_ENTITY = "climate_entity"
CONF_IR_POWER_ON = "ir_power_on"
CONF_IR_POWER_OFF = "ir_power_off"
CONF_IR_MODE_COOL = "ir_mode_cool"
CONF_IR_TEMPERATURE_CONTROL = "ir_temperature_control"
CONF_IR_TEMPERATURE_SCRIPT = "ir_temperature_script"
CONF_IR_TEMPERATURE_FIELD = "ir_temperature_field"
CONF_IR_TEMP_UP = "ir_temp_up"
CONF_IR_TEMP_DOWN = "ir_temp_down"
CONF_IR_FAN_AUTO = "ir_fan_auto"
CONF_IR_FAN_LOW = "ir_fan_low"
CONF_IR_FAN_MEDIUM = "ir_fan_medium"
CONF_IR_FAN_HIGH = "ir_fan_high"
CONF_CONFIRM = "confirm"

CONF_DRY_RUN = "dry_run"
CONF_ENABLE_PRESENCE = "enable_presence"
CONF_ENABLE_DOOR = "enable_door"
CONF_ENABLE_LIGHTING = "enable_lighting"
CONF_ENABLE_FAN = "enable_fan"
CONF_ENABLE_CLIMATE = "enable_climate"
CONF_PRESENCE_MODE = "presence_mode"
CONF_PRESENCE_PRIMARY = "presence_primary"
CONF_MOTION_MODE = "motion_mode"
CONF_MOTION_PRIMARY = "motion_primary"
CONF_TEMPERATURE_MODE = "temperature_mode"
CONF_TEMPERATURE_PRIMARY = "temperature_primary"
CONF_ILLUMINANCE_MODE = "illuminance_mode"
CONF_ILLUMINANCE_PRIMARY = "illuminance_primary"
CONF_LIGHT_ON_LUX = "light_on_lux"
CONF_LIGHT_OFF_LUX = "light_off_lux"
CONF_FAN_ON_TEMP = "fan_on_temperature"
CONF_FAN_OFF_TEMP = "fan_off_temperature"
CONF_CLIMATE_ON_TEMP = "climate_on_temperature"
CONF_CLIMATE_OFF_TEMP = "climate_off_temperature"
CONF_NO_OCCUPANCY_DELAY = "no_occupancy_delay"
CONF_DOOR_OPEN_DELAY = "door_open_delay"
CONF_STARTUP_HOLD = "startup_hold"

ATTR_MODULE = "module"
ATTR_INTENT = "intent"
ATTR_REASON = "reason"
ATTR_DETAILS = "details"

SIGNAL_RUNTIME_UPDATED = f"{DOMAIN}_runtime_updated"


class ACControlType(StrEnum):
    """Supported air-conditioner control types."""

    NONE = "none"
    CLIMATE = "climate"
    IR_SCRIPTS = "ir_scripts"


class IRTemperatureControl(StrEnum):
    """Supported IR temperature control styles."""

    NONE = "none"
    DIRECT_SCRIPT = "direct_script"
    UP_DOWN = "up_down"


class BinaryCombineMode(StrEnum):
    """Combination modes for binary sensors."""

    OR = "or"
    AND = "and"
    PRIMARY = "primary"


class NumericCombineMode(StrEnum):
    """Combination modes for numeric sensors."""

    PRIMARY = "primary"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    AVERAGE = "average"


class ModuleName(StrEnum):
    """Logical modules managed by the integration."""

    PRESENCE = "presence"
    DOOR = "door"
    LIGHTING = "lighting"
    FAN = "fan"
    CLIMATE = "climate"


class Intent(StrEnum):
    """Dry-run intents."""

    NONE = "none"
    TURN_ON_LIGHT = "turn_on_light"
    TURN_OFF_LIGHT = "turn_off_light"
    TURN_ON_FAN = "turn_on_fan"
    TURN_OFF_FAN = "turn_off_fan"
    TURN_ON_CLIMATE = "turn_on_climate"
    TURN_OFF_CLIMATE = "turn_off_climate"
    SEND_IR_POWER_ON = "send_ir_power_on"
    SEND_IR_POWER_OFF = "send_ir_power_off"
