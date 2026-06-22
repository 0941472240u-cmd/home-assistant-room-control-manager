"""Reusable Home Assistant selectors."""

from __future__ import annotations

from homeassistant.helpers.selector import (
    AreaSelector,
    AreaSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)


def room_name_selector() -> TextSelector:
    """Create a room-name selector."""

    return TextSelector(TextSelectorConfig(type="text"))


def area_selector() -> AreaSelector:
    """Create an optional area selector."""

    return AreaSelector(AreaSelectorConfig(multiple=False))


def entity_selector(
    domains: list[str],
    *,
    device_classes: list[str] | None = None,
    multiple: bool = False,
    include_entities: list[str] | None = None,
) -> EntitySelector:
    """Create an entity selector filtered by domain and optional device class."""

    config: EntitySelectorConfig = {
        "multiple": multiple,
        "filter": [{"domain": domains, **({"device_class": device_classes} if device_classes else {})}],
    }
    if include_entities is not None:
        config["include_entities"] = include_entities
    return EntitySelector(config)


def choice_selector(options: list[str], *, translation_key: str | None = None) -> SelectSelector:
    """Create a localized dropdown selector."""

    config: SelectSelectorConfig = {
        "options": options,
        "mode": SelectSelectorMode.DROPDOWN,
    }
    if translation_key is not None:
        config["translation_key"] = translation_key
    return SelectSelector(config)


def numeric_selector(minimum: float, maximum: float, step: float) -> NumberSelector:
    """Create a numeric selector."""

    return NumberSelector(
        NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
            mode=NumberSelectorMode.BOX,
        )
    )
