"""Room Control Manager custom integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .runtime import RoomRuntime


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one independently configured room."""

    existing = getattr(entry, "runtime_data", None)
    if isinstance(existing, RoomRuntime):
        await existing.async_stop()
    runtime = RoomRuntime(hass, entry)
    entry.runtime_data = runtime
    try:
        await runtime.async_start()
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await runtime.async_stop()
        entry.runtime_data = None
        raise
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload one room and every listener it owns."""

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False
    runtime = getattr(entry, "runtime_data", None)
    if isinstance(runtime, RoomRuntime):
        await runtime.async_stop()
    entry.runtime_data = None
    return True
