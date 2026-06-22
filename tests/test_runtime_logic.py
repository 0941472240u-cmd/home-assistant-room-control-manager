from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from types import SimpleNamespace

from homeassistant.util import dt as dt_util

from custom_components.room_control_manager.configuration.defaults import build_default_options
from custom_components.room_control_manager.configuration.ownership import check_ownership
from custom_components.room_control_manager.const import (
    CONF_AC_CONTROL_TYPE,
    CONF_CLIMATE_ENTITY,
    CONF_ENABLE_CLIMATE,
    CONF_ENABLE_DOOR,
    CONF_ENABLE_FAN,
    CONF_ENABLE_LIGHTING,
    CONF_ENABLE_PRESENCE,
    CONF_FAN_ENTITY,
    CONF_ILLUMINANCE_SENSORS,
    CONF_LIGHT_ENTITY,
    CONF_PRESENCE_SENSORS,
    CONF_STARTUP_HOLD,
    CONF_TEMPERATURE_SENSORS,
    ACControlType,
    Intent,
    ModuleName,
)
from custom_components.room_control_manager.dry_run.evaluator import DryRunEvaluator
from custom_components.room_control_manager.models import ModuleStatus
from custom_components.room_control_manager.monitoring.availability import assess_module_statuses


@dataclass
class FakeState:
    state: str


class FakeStates:
    def __init__(self, states: dict[str, str]) -> None:
        self._states = {entity_id: FakeState(state) for entity_id, state in states.items()}

    def get(self, entity_id: str) -> FakeState | None:
        return self._states.get(entity_id)

    def __getitem__(self, entity_id: str) -> FakeState:
        return self._states[entity_id]


class FakeConfigEntries:
    def __init__(self, entries: list[SimpleNamespace]) -> None:
        self._entries = entries

    def async_entries(self, domain: str) -> list[SimpleNamespace]:
        return self._entries


def test_defaults_enable_only_configured_modules() -> None:
    empty = build_default_options({})
    assert empty[CONF_ENABLE_PRESENCE] is False
    assert empty[CONF_ENABLE_DOOR] is False
    assert empty[CONF_ENABLE_LIGHTING] is False
    assert empty[CONF_ENABLE_FAN] is False
    assert empty[CONF_ENABLE_CLIMATE] is False

    configured = build_default_options(
        {
            CONF_PRESENCE_SENSORS: ["binary_sensor.generic_presence"],
            CONF_LIGHT_ENTITY: "light.generic_light",
            CONF_FAN_ENTITY: "fan.generic_fan",
            CONF_AC_CONTROL_TYPE: ACControlType.CLIMATE,
        }
    )
    assert configured[CONF_ENABLE_PRESENCE] is True
    assert configured[CONF_ENABLE_LIGHTING] is True
    assert configured[CONF_ENABLE_FAN] is True
    assert configured[CONF_ENABLE_CLIMATE] is True


def test_unavailable_entity_isolates_only_related_modules() -> None:
    data = {
        CONF_PRESENCE_SENSORS: ["binary_sensor.generic_presence"],
        CONF_TEMPERATURE_SENSORS: ["sensor.generic_temperature"],
        CONF_ILLUMINANCE_SENSORS: ["sensor.generic_illuminance"],
        CONF_LIGHT_ENTITY: "light.generic_light",
        CONF_FAN_ENTITY: "fan.generic_fan",
    }
    options = build_default_options(data)
    hass = SimpleNamespace(
        states=FakeStates(
            {
                "binary_sensor.generic_presence": "on",
                "sensor.generic_temperature": "29",
                "sensor.generic_illuminance": "unavailable",
                "light.generic_light": "off",
                "fan.generic_fan": "off",
            }
        )
    )
    statuses = assess_module_statuses(hass, data, options)
    assert statuses[ModuleName.LIGHTING].ready is False
    assert statuses[ModuleName.FAN].ready is True
    assert statuses[ModuleName.PRESENCE].ready is True


def test_ownership_shares_sensors_but_blocks_actuators() -> None:
    existing = SimpleNamespace(
        entry_id="entry-existing",
        data={
            CONF_PRESENCE_SENSORS: ["binary_sensor.shared_presence"],
            CONF_LIGHT_ENTITY: "light.owned_light",
        },
    )
    hass = SimpleNamespace(config_entries=FakeConfigEntries([existing]))
    result = check_ownership(
        hass,
        {
            CONF_PRESENCE_SENSORS: ["binary_sensor.shared_presence"],
            CONF_LIGHT_ENTITY: "light.owned_light",
        },
    )
    assert result.shared_sensors == ("binary_sensor.shared_presence",)
    assert result.conflicts == ("light.owned_light",)


def test_evaluator_reports_intent_without_services_object() -> None:
    data = {
        CONF_PRESENCE_SENSORS: ["binary_sensor.generic_presence"],
        CONF_TEMPERATURE_SENSORS: ["sensor.generic_temperature"],
        CONF_ILLUMINANCE_SENSORS: ["sensor.generic_illuminance"],
        CONF_LIGHT_ENTITY: "light.generic_light",
        CONF_FAN_ENTITY: "fan.generic_fan",
        CONF_AC_CONTROL_TYPE: ACControlType.CLIMATE,
        CONF_CLIMATE_ENTITY: "climate.generic_ac",
    }
    options = build_default_options(data)
    options[CONF_STARTUP_HOLD] = 0
    hass = SimpleNamespace(
        states=FakeStates(
            {
                "binary_sensor.generic_presence": "on",
                "sensor.generic_temperature": "31",
                "sensor.generic_illuminance": "10",
                "light.generic_light": "off",
                "fan.generic_fan": "off",
                "climate.generic_ac": "off",
            }
        )
    )
    statuses = {module: ModuleStatus(module, True, True, ()) for module in ModuleName}
    evaluator = DryRunEvaluator(hass)
    decision = evaluator.evaluate(
        data,
        options,
        statuses,
        now=dt_util.utcnow() + timedelta(seconds=1),
    )
    intents = {action.intent for action in decision.actions}
    assert Intent.TURN_ON_LIGHT in intents
    assert Intent.TURN_ON_FAN in intents
    assert Intent.TURN_ON_CLIMATE in intents
