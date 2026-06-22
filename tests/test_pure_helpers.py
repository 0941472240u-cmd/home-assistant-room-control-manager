from __future__ import annotations

from custom_components.room_control_manager.configuration.normalization import compact_mapping, normalize_entity_list
from custom_components.room_control_manager.configuration.ownership import selected_actuators, selected_sensors
from custom_components.room_control_manager.const import CONF_FAN_ENTITY, CONF_LIGHT_ENTITY, CONF_PRESENCE_SENSORS


def test_normalize_entity_list() -> None:
    assert normalize_entity_list(["sensor.alpha", "sensor.alpha", "sensor.beta", ""]) == ["sensor.alpha", "sensor.beta"]
    assert normalize_entity_list(None) == []


def test_compact_mapping_keeps_false_and_zero() -> None:
    assert compact_mapping({"empty": "", "none": None, "false": False, "zero": 0}) == {"false": False, "zero": 0}


def test_ownership_role_sets() -> None:
    data = {
        CONF_LIGHT_ENTITY: "light.generic_room",
        CONF_FAN_ENTITY: "fan.generic_room",
        CONF_PRESENCE_SENSORS: ["binary_sensor.generic_presence"],
    }
    assert selected_actuators(data) == {"light.generic_room", "fan.generic_room"}
    assert selected_sensors(data) == {"binary_sensor.generic_presence"}
