"""Status sensors for Room Control Manager."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import RoomControlEntity
from .runtime import RoomRuntime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    runtime: RoomRuntime = entry.runtime_data
    async_add_entities(
        [
            RoomConfigurationStatusSensor(runtime),
            RoomLastDecisionSensor(runtime),
            RoomLastReasonSensor(runtime),
            RoomReadyModulesSensor(runtime),
            RoomProblemModulesSensor(runtime),
        ]
    )


class _RuntimeSensor(RoomControlEntity, SensorEntity):
    """Base class for read-only runtime sensor entities."""

    _attr_should_poll = False


class RoomConfigurationStatusSensor(_RuntimeSensor):
    _attr_translation_key = "configuration_status"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "configuration_status")

    @property
    def native_value(self) -> str:
        if not self.runtime.statuses:
            return "initializing"
        enabled = [status for status in self.runtime.statuses.values() if status.enabled]
        if enabled and all(status.ready for status in enabled):
            return "ready"
        if any(status.ready for status in enabled):
            return "degraded"
        return "problem"


class RoomLastDecisionSensor(_RuntimeSensor):
    _attr_translation_key = "last_decision"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "last_decision")

    @property
    def native_value(self) -> str:
        return self.runtime.decision.summary if self.runtime.decision else "not_evaluated"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        decision = self.runtime.decision
        if decision is None:
            return {}
        return {
            "evaluated_at": decision.evaluated_at.isoformat(),
            "actions": [
                {
                    "module": action.module.value,
                    "intent": action.intent.value,
                    "reason": action.reason,
                    "target_role": action.target_role,
                    "details": action.details,
                }
                for action in decision.actions
            ],
        }


class RoomLastReasonSensor(_RuntimeSensor):
    _attr_translation_key = "last_reason"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "last_reason")

    @property
    def native_value(self) -> str:
        return self.runtime.decision.reason if self.runtime.decision else "not_evaluated"


class RoomReadyModulesSensor(_RuntimeSensor):
    _attr_translation_key = "ready_modules"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "ready_modules")

    @property
    def native_value(self) -> str:
        ready = [module.value for module, status in self.runtime.statuses.items() if status.ready]
        return ", ".join(ready) if ready else "none"


class RoomProblemModulesSensor(_RuntimeSensor):
    _attr_translation_key = "problem_modules"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "problem_modules")

    @property
    def native_value(self) -> str:
        problem = [
            module.value for module, status in self.runtime.statuses.items() if status.enabled and not status.ready
        ]
        return ", ".join(problem) if problem else "none"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            module.value: list(status.problems) for module, status in self.runtime.statuses.items() if status.problems
        }
