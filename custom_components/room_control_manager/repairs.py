"""Repair issue synchronization."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN, ModuleName
from .models import ModuleStatus


def _issue_id(entry_id: str, module: ModuleName) -> str:
    digest = hashlib.sha256(entry_id.encode()).hexdigest()[:12]
    return f"{digest}_{module.value}_configuration"


async def async_sync_repairs(
    hass: HomeAssistant,
    entry_id: str,
    room_name: str,
    statuses: Mapping[ModuleName, ModuleStatus],
) -> None:
    """Create issues for broken modules and remove resolved issues."""

    for module, status in statuses.items():
        issue_id = _issue_id(entry_id, module)
        actionable = (
            status.enabled
            and bool(status.problems)
            and any(problem.startswith(("missing:", "unavailable:", "not_configured:")) for problem in status.problems)
        )
        if actionable:
            ir.async_create_issue(
                hass,
                DOMAIN,
                issue_id,
                is_fixable=False,
                is_persistent=False,
                severity=ir.IssueSeverity.ERROR,
                translation_key="module_configuration_problem",
                translation_placeholders={
                    "room": room_name,
                    "module": module.value,
                    "problem": ", ".join(problem.split(":", 1)[0] for problem in status.problems),
                },
            )
        else:
            ir.async_delete_issue(hass, DOMAIN, issue_id)
