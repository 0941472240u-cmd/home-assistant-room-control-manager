"""Data models for Room Control Manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .const import Intent, ModuleName


@dataclass(slots=True, frozen=True)
class ModuleStatus:
    """Availability status for one logical module."""

    name: ModuleName
    enabled: bool
    ready: bool
    problems: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class IntendedAction:
    """One action proposed by the dry-run evaluator."""

    module: ModuleName
    intent: Intent
    reason: str
    target_role: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class DryRunDecision:
    """Result of one dry-run evaluation cycle."""

    evaluated_at: datetime
    effective_occupancy: bool | None
    temperature: float | None
    illuminance: float | None
    door_open: bool | None
    actions: tuple[IntendedAction, ...]
    summary: str
    reason: str


@dataclass(slots=True, frozen=True)
class OwnershipResult:
    """Ownership validation result."""

    conflicts: tuple[str, ...] = ()
    shared_sensors: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class ValidationResult:
    """Configuration validation result."""

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
