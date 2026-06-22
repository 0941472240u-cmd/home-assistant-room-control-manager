"""Base entity for Room Control Manager."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, VERSION
from .runtime import RoomRuntime


class RoomControlEntity(Entity):
    """Base entity linked to one room runtime."""

    _attr_has_entity_name = True

    def __init__(self, runtime: RoomRuntime, key: str) -> None:
        self.runtime = runtime
        self._key = key
        room_id = str(runtime.entry.data["room_id"])
        self._attr_unique_id = f"{room_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, room_id)},
            name=runtime.entry.title,
            manufacturer="Room Control Manager",
            model="Dry Run Controller",
            sw_version=VERSION,
            configuration_url=None,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, self.runtime.signal, self._handle_update))

    def _handle_update(self) -> None:
        self.async_write_ha_state()
