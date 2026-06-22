"""Per-config-entry runtime management."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers.event import async_track_state_change_event

from .configuration.defaults import build_default_options
from .configuration.ownership import selected_actuators, selected_sensors
from .const import CONF_ROOM_NAME, SIGNAL_RUNTIME_UPDATED
from .dry_run.evaluator import DryRunEvaluator
from .models import DryRunDecision, ModuleStatus
from .monitoring.availability import assess_module_statuses
from .repairs import async_sync_repairs

_LOGGER = logging.getLogger(__name__)


class RoomRuntime:
    """Own listeners and state for one room config entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.evaluator = DryRunEvaluator(hass)
        self.statuses: dict[Any, ModuleStatus] = {}
        self.decision: DryRunDecision | None = None
        self._unsubscribers: list[Callable[[], None]] = []
        self._refresh_lock = asyncio.Lock()
        self._stopping = False
        self._started = False

    @property
    def signal(self) -> str:
        return f"{SIGNAL_RUNTIME_UPDATED}_{self.entry.entry_id}"

    @property
    def selected_entities(self) -> set[str]:
        return selected_sensors(self.entry.data) | selected_actuators(self.entry.data)

    def effective_options(self) -> dict[str, Any]:
        options = build_default_options(self.entry.data)
        options.update(self.entry.options)
        options["dry_run"] = True
        return options

    async def async_start(self) -> None:
        """Start listeners and perform initial evaluation."""

        if self._started:
            return
        self._started = True
        entity_ids = sorted(self.selected_entities)
        if entity_ids:
            self._unsubscribers.append(async_track_state_change_event(self.hass, entity_ids, self._state_changed))
        self._unsubscribers.append(self.hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, self._registry_changed))
        await self.async_refresh("startup")

    async def async_stop(self) -> None:
        """Stop all listeners before unloading the config entry."""

        self._stopping = True
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()
        async with self._refresh_lock:
            self._started = False

    @callback
    def _state_changed(self, event: Event) -> None:
        if not self._stopping:
            self.hass.async_create_task(self.async_refresh("state_changed"))

    @callback
    def _registry_changed(self, event: Event) -> None:
        data = event.data
        candidates = {data.get("entity_id"), data.get("old_entity_id"), data.get("new_entity_id")}
        if self.selected_entities.intersection(item for item in candidates if item) and not self._stopping:
            self.hass.async_create_task(self.async_refresh("entity_registry_changed"))

    async def async_refresh(self, trigger: str) -> None:
        """Refresh availability, repairs, and dry-run decision atomically."""

        if self._stopping:
            return
        async with self._refresh_lock:
            if self._stopping:
                return
            options = self.effective_options()
            self.statuses = assess_module_statuses(self.hass, self.entry.data, options)
            await async_sync_repairs(
                self.hass,
                self.entry.entry_id,
                str(self.entry.data.get(CONF_ROOM_NAME, self.entry.title)),
                self.statuses,
            )
            self.decision = self.evaluator.evaluate(self.entry.data, options, self.statuses)
            _LOGGER.info(
                "Dry-run evaluation for %s (%s): %s; reason=%s",
                self.entry.title,
                trigger,
                self.decision.summary,
                self.decision.reason,
            )
            async_dispatcher_send(self.hass, self.signal)
