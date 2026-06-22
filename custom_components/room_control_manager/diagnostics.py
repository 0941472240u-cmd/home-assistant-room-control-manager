"""Diagnostics support with entity identifiers redacted."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION
from .runtime import RoomRuntime


def _token(value: str) -> str:
    return f"entity-{hashlib.sha256(value.encode()).hexdigest()[:10]}"


def _redact_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        if key in {"room_name", "area_id"}:
            redacted[key] = "<redacted>"
        elif isinstance(value, str) and "." in value:
            redacted[key] = _token(value)
        elif isinstance(value, list):
            redacted[key] = [_token(item) if isinstance(item, str) and "." in item else item for item in value]
        else:
            redacted[key] = value
    return redacted


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    runtime: RoomRuntime = entry.runtime_data
    decision = runtime.decision
    return {
        "domain": DOMAIN,
        "version": VERSION,
        "entry_version": entry.version,
        "entry_minor_version": entry.minor_version,
        "data": _redact_mapping(entry.data),
        "options": _redact_mapping(runtime.effective_options()),
        "module_statuses": {
            module.value: {
                "enabled": status.enabled,
                "ready": status.ready,
                "problem_types": [problem.split(":", 1)[0] for problem in status.problems],
            }
            for module, status in runtime.statuses.items()
        },
        "decision": None
        if decision is None
        else {
            "evaluated_at": decision.evaluated_at.isoformat(),
            "summary": decision.summary,
            "reason": decision.reason,
            "effective_occupancy": decision.effective_occupancy,
            "temperature": decision.temperature,
            "illuminance": decision.illuminance,
            "door_open": decision.door_open,
            "actions": [
                {"module": action.module.value, "intent": action.intent.value, "reason": action.reason}
                for action in decision.actions
            ],
        },
    }
