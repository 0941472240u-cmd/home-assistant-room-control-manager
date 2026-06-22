"""Binary status sensors for Room Control Manager."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
            RoomDryRunBinarySensor(runtime),
            RoomConfigurationProblemBinarySensor(runtime),
            RoomEffectiveOccupancyBinarySensor(runtime),
        ]
    )


class _RuntimeBinarySensor(RoomControlEntity, BinarySensorEntity):
    """Base class for read-only runtime binary sensor entities."""

    _attr_should_poll = False


class RoomDryRunBinarySensor(_RuntimeBinarySensor):
    _attr_translation_key = "dry_run"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "dry_run")

    @property
    def is_on(self) -> bool:
        return True


class RoomConfigurationProblemBinarySensor(_RuntimeBinarySensor):
    _attr_translation_key = "configuration_problem"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "configuration_problem")

    @property
    def is_on(self) -> bool:
        return any(status.enabled and not status.ready for status in self.runtime.statuses.values())


class RoomEffectiveOccupancyBinarySensor(_RuntimeBinarySensor):
    _attr_translation_key = "effective_occupancy"

    def __init__(self, runtime: RoomRuntime) -> None:
        super().__init__(runtime, "effective_occupancy")

    @property
    def is_on(self) -> bool | None:
        return self.runtime.decision.effective_occupancy if self.runtime.decision else None
