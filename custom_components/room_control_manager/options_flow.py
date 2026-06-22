"""Options flow for Room Control Manager."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlowResult, OptionsFlowWithReload

from .configuration.defaults import build_default_options
from .configuration.normalization import merge_values
from .configuration.schemas import (
    binary_options_schema,
    modules_options_schema,
    numeric_options_schema,
    options_review_schema,
    thresholds_options_schema,
)
from .configuration.validation import validate_options
from .const import CONF_CONFIRM, CONF_DRY_RUN


class RoomControlOptionsFlow(OptionsFlowWithReload):
    """Edit behavior while relying on one framework-managed reload."""

    def __init__(self) -> None:
        self._values: dict[str, Any] = {}

    def _current(self) -> dict[str, Any]:
        current = build_default_options(self.config_entry.data)
        current.update(self.config_entry.options)
        current.update(self._values)
        current[CONF_DRY_RUN] = True
        return current

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self.async_step_modules(user_input)

    async def async_step_modules(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._values = merge_values(self._values, user_input)
            return await self.async_step_binary()
        return self.async_show_form(step_id="modules", data_schema=modules_options_schema(self._current()))

    async def async_step_binary(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._values = merge_values(self._values, user_input)
            return await self.async_step_numeric()
        return self.async_show_form(
            step_id="binary",
            data_schema=binary_options_schema(self._current(), self.config_entry.data),
        )

    async def async_step_numeric(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._values = merge_values(self._values, user_input)
            return await self.async_step_thresholds()
        return self.async_show_form(
            step_id="numeric",
            data_schema=numeric_options_schema(self._current(), self.config_entry.data),
        )

    async def async_step_thresholds(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._values = merge_values(self._values, user_input)
            return await self.async_step_review()
        return self.async_show_form(step_id="thresholds", data_schema=thresholds_options_schema(self._current()))

    async def async_step_review(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        current = self._current()
        validation = validate_options(self.config_entry.data, current)
        if user_input is not None:
            if not user_input.get(CONF_CONFIRM):
                errors["base"] = "confirmation_required"
            elif validation.errors:
                errors["base"] = validation.errors[0].split(":", 1)[0]
            else:
                current[CONF_DRY_RUN] = True
                return self.async_create_entry(data=current)
        return self.async_show_form(
            step_id="review",
            data_schema=options_review_schema(),
            errors=errors,
            description_placeholders={
                "warnings": ", ".join(validation.warnings) if validation.warnings else "none",
                "mode": "Dry Run",
            },
        )
