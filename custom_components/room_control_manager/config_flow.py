"""Config and reconfigure flows for Room Control Manager."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from homeassistant import config_entries
from homeassistant.core import callback

from .configuration.defaults import build_default_options
from .configuration.normalization import merge_values, normalize_entity_list
from .configuration.ownership import check_ownership, get_ownership_lock
from .configuration.schemas import (
    actuators_schema,
    climate_schema,
    ir_schema,
    review_schema,
    room_schema,
    sensors_schema,
)
from .configuration.validation import validate_installation_data
from .const import (
    CONF_AC_CONTROL_TYPE,
    CONF_CONFIRM,
    CONF_IR_FAN_AUTO,
    CONF_IR_FAN_HIGH,
    CONF_IR_FAN_LOW,
    CONF_IR_FAN_MEDIUM,
    CONF_IR_MODE_COOL,
    CONF_IR_POWER_OFF,
    CONF_IR_POWER_ON,
    CONF_IR_TEMP_DOWN,
    CONF_IR_TEMP_UP,
    CONF_IR_TEMPERATURE_CONTROL,
    CONF_IR_TEMPERATURE_FIELD,
    CONF_IR_TEMPERATURE_SCRIPT,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONFIG_ENTRY_MINOR_VERSION,
    CONFIG_ENTRY_VERSION,
    DOMAIN,
    ACControlType,
)
from .options_flow import RoomControlOptionsFlow

IR_KEYS = (
    CONF_IR_POWER_ON,
    CONF_IR_POWER_OFF,
    CONF_IR_MODE_COOL,
    CONF_IR_TEMPERATURE_CONTROL,
    CONF_IR_TEMPERATURE_SCRIPT,
    CONF_IR_TEMPERATURE_FIELD,
    CONF_IR_TEMP_UP,
    CONF_IR_TEMP_DOWN,
    CONF_IR_FAN_AUTO,
    CONF_IR_FAN_LOW,
    CONF_IR_FAN_MEDIUM,
    CONF_IR_FAN_HIGH,
)


class RoomControlManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create and reconfigure independent room entries."""

    VERSION = CONFIG_ENTRY_VERSION
    MINOR_VERSION = CONFIG_ENTRY_MINOR_VERSION

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._reconfigure_entry: config_entries.ConfigEntry | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> RoomControlOptionsFlow:
        return RoomControlOptionsFlow()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        return await self.async_step_room(user_input)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        self._reconfigure_entry = self._get_reconfigure_entry()
        self._data = dict(self._reconfigure_entry.data)
        await self.async_set_unique_id(self._reconfigure_entry.unique_id)
        self._abort_if_unique_id_mismatch()
        return await self.async_step_room(user_input)

    async def async_step_room(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if not str(user_input.get(CONF_ROOM_NAME, "")).strip():
                errors[CONF_ROOM_NAME] = "room_name_required"
            else:
                self._data = merge_values(self._data, user_input)
                return await self.async_step_sensors()
        return self.async_show_form(step_id="room", data_schema=room_schema(self._data), errors=errors)

    async def async_step_sensors(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            for key, value in user_input.items():
                if key.endswith("_sensors"):
                    user_input[key] = normalize_entity_list(value)
            self._data = merge_values(self._data, user_input)
            return await self.async_step_actuators()
        return self.async_show_form(step_id="sensors", data_schema=sensors_schema(self._data))

    async def async_step_actuators(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._data = merge_values(self._data, user_input)
            ac_type = self._data.get(CONF_AC_CONTROL_TYPE, ACControlType.NONE)
            if ac_type == ACControlType.CLIMATE:
                for key in IR_KEYS:
                    self._data.pop(key, None)
                return await self.async_step_climate()
            if ac_type == ACControlType.IR_SCRIPTS:
                self._data.pop("climate_entity", None)
                return await self.async_step_ir()
            self._data.pop("climate_entity", None)
            for key in IR_KEYS:
                self._data.pop(key, None)
            return await self.async_step_review()
        return self.async_show_form(step_id="actuators", data_schema=actuators_schema(self._data))

    async def async_step_climate(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._data = merge_values(self._data, user_input)
            return await self.async_step_review()
        return self.async_show_form(step_id="climate", data_schema=climate_schema(self._data))

    async def async_step_ir(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._data = merge_values(self._data, user_input)
            return await self.async_step_review()
        return self.async_show_form(step_id="ir", data_schema=ir_schema(self._data))

    async def async_step_review(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        validation = validate_installation_data(self.hass, self._data)
        ownership = check_ownership(
            self.hass,
            self._data,
            exclude_entry_id=self._reconfigure_entry.entry_id if self._reconfigure_entry else None,
        )
        if ownership.conflicts:
            errors["base"] = "actuator_in_use"
        elif validation.errors:
            errors["base"] = validation.errors[0].split(":", 1)[0]
        if user_input is not None and not errors:
            if not user_input.get(CONF_CONFIRM):
                errors["base"] = "confirmation_required"
            else:
                async with get_ownership_lock(self.hass):
                    final_ownership = check_ownership(
                        self.hass,
                        self._data,
                        exclude_entry_id=self._reconfigure_entry.entry_id if self._reconfigure_entry else None,
                    )
                    if final_ownership.conflicts:
                        errors["base"] = "actuator_in_use"
                    elif self._reconfigure_entry is not None:
                        return self.async_update_reload_and_abort(
                            self._reconfigure_entry,
                            title=str(self._data[CONF_ROOM_NAME]),
                            data=self._data,
                            reload_even_if_entry_is_unchanged=False,
                        )
                    else:
                        room_id = uuid4().hex
                        self._data[CONF_ROOM_ID] = room_id
                        await self.async_set_unique_id(room_id)
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title=str(self._data[CONF_ROOM_NAME]),
                            data=self._data,
                            options=build_default_options(self._data),
                        )
        return self.async_show_form(
            step_id="review",
            data_schema=review_schema(),
            errors=errors,
            description_placeholders={
                "warnings": ", ".join(validation.warnings) if validation.warnings else "none",
                "shared_sensors": str(len(ownership.shared_sensors)),
                "conflicts": str(len(ownership.conflicts)),
                "mode": "Dry Run",
            },
        )
