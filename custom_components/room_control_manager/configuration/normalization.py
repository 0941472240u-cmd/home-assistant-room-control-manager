"""Normalize selector and config-entry values."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def normalize_entity_list(value: Any) -> list[str]:
    """Return an ordered, duplicate-free list of non-empty entity IDs."""

    if value is None or value == "":
        return []
    items: Iterable[Any] = value if isinstance(value, list | tuple | set) else [value]
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, str) or not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def compact_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    """Remove empty optional values while preserving false and zero."""

    compacted: dict[str, Any] = {}
    for key, value in data.items():
        if value is None or value == "" or value == []:
            continue
        compacted[key] = value
    return compacted


def merge_values(base: Mapping[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    """Merge form values into existing data and remove cleared optional values."""

    merged = dict(base)
    for key, value in updates.items():
        if value is None or value == "" or value == []:
            merged.pop(key, None)
        else:
            merged[key] = value
    return merged
