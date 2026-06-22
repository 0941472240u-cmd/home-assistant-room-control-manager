"""Evaluate intended room-control actions without executing services."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from statistics import fmean
from typing import Any

from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.util import dt as dt_util

from ..configuration.normalization import normalize_entity_list
from ..const import *  # noqa: F403
from ..models import DryRunDecision, IntendedAction, ModuleStatus


class DryRunEvaluator:
    """Stateful, service-free evaluator."""

    def __init__(self, hass: Any) -> None:
        self._hass = hass
        self._condition_since: dict[str, datetime] = {}
        self._started_at = dt_util.utcnow()

    def _binary(self, entity_ids: list[str], mode: str, primary: str | None) -> bool | None:
        if not entity_ids:
            return None
        states: dict[str, bool] = {}
        unavailable = False
        for entity_id in entity_ids:
            state = self._hass.states.get(entity_id)
            if state is None or state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
                unavailable = True
                continue
            states[entity_id] = state.state == STATE_ON
        if mode == BinaryCombineMode.PRIMARY:
            return states.get(primary) if primary else None
        if mode == BinaryCombineMode.OR:
            if any(states.values()):
                return True
            return None if unavailable else False
        if mode == BinaryCombineMode.AND:
            if not states or unavailable:
                return None
            return all(states.values())
        return None

    def _numeric(self, entity_ids: list[str], mode: str, primary: str | None) -> float | None:
        values: dict[str, float] = {}
        for entity_id in entity_ids:
            state = self._hass.states.get(entity_id)
            if state is None or state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
                continue
            try:
                values[entity_id] = float(state.state)
            except (TypeError, ValueError):
                continue
        if not values:
            return None
        if mode == NumericCombineMode.PRIMARY:
            return values.get(primary) if primary else None
        if mode == NumericCombineMode.MINIMUM:
            return min(values.values())
        if mode == NumericCombineMode.MAXIMUM:
            return max(values.values())
        if mode == NumericCombineMode.AVERAGE:
            return fmean(values.values())
        return None

    def _delayed(self, key: str, condition: bool, seconds: float, now: datetime) -> bool:
        if not condition:
            self._condition_since.pop(key, None)
            return False
        since = self._condition_since.setdefault(key, now)
        return now - since >= timedelta(seconds=max(0, seconds))

    def evaluate(
        self,
        data: Mapping[str, Any],
        options: Mapping[str, Any],
        statuses: Mapping[ModuleName, ModuleStatus],
        *,
        now: datetime | None = None,
    ) -> DryRunDecision:
        """Return intended actions only; this method never calls Home Assistant services."""

        now = now or dt_util.utcnow()
        startup_hold = max(0.0, float(options.get(CONF_STARTUP_HOLD, 0)))
        if now - self._started_at < timedelta(seconds=startup_hold):
            return DryRunDecision(
                now,
                None,
                None,
                None,
                None,
                (),
                Intent.NONE.value,
                "startup_hold_active",
            )
        presence = self._binary(
            normalize_entity_list(data.get(CONF_PRESENCE_SENSORS)),
            str(options.get(CONF_PRESENCE_MODE, BinaryCombineMode.OR)),
            options.get(CONF_PRESENCE_PRIMARY),
        )
        motion = self._binary(
            normalize_entity_list(data.get(CONF_MOTION_SENSORS)),
            str(options.get(CONF_MOTION_MODE, BinaryCombineMode.OR)),
            options.get(CONF_MOTION_PRIMARY),
        )
        if presence is True or motion is True:
            occupied: bool | None = True
        elif presence is False and motion is False:
            occupied = False
        elif presence is not None:
            occupied = presence
        else:
            occupied = motion

        temperature = self._numeric(
            normalize_entity_list(data.get(CONF_TEMPERATURE_SENSORS)),
            str(options.get(CONF_TEMPERATURE_MODE, NumericCombineMode.AVERAGE)),
            options.get(CONF_TEMPERATURE_PRIMARY),
        )
        illuminance = self._numeric(
            normalize_entity_list(data.get(CONF_ILLUMINANCE_SENSORS)),
            str(options.get(CONF_ILLUMINANCE_MODE, NumericCombineMode.PRIMARY)),
            options.get(CONF_ILLUMINANCE_PRIMARY),
        )
        door_open = self._binary(
            normalize_entity_list(data.get(CONF_DOOR_SENSOR)), BinaryCombineMode.PRIMARY, data.get(CONF_DOOR_SENSOR)
        )
        vacant_long_enough = self._delayed(
            "vacant",
            occupied is False,
            float(options.get(CONF_NO_OCCUPANCY_DELAY, 0)),
            now,
        )
        door_open_long_enough = self._delayed(
            "door_open",
            door_open is True,
            float(options.get(CONF_DOOR_OPEN_DELAY, 0)),
            now,
        )

        actions: list[IntendedAction] = []
        if statuses[ModuleName.LIGHTING].ready and occupied is not None and illuminance is not None:
            if occupied and illuminance <= float(options[CONF_LIGHT_ON_LUX]):
                actions.append(
                    IntendedAction(
                        ModuleName.LIGHTING, Intent.TURN_ON_LIGHT, "occupied_and_dark", "light", {"lux": illuminance}
                    )
                )
            elif vacant_long_enough or illuminance >= float(options[CONF_LIGHT_OFF_LUX]):
                actions.append(
                    IntendedAction(
                        ModuleName.LIGHTING, Intent.TURN_OFF_LIGHT, "vacant_or_bright", "light", {"lux": illuminance}
                    )
                )

        if statuses[ModuleName.FAN].ready and temperature is not None:
            if occupied and temperature >= float(options[CONF_FAN_ON_TEMP]):
                actions.append(
                    IntendedAction(
                        ModuleName.FAN, Intent.TURN_ON_FAN, "occupied_and_hot", "fan", {"temperature": temperature}
                    )
                )
            elif vacant_long_enough or temperature <= float(options[CONF_FAN_OFF_TEMP]):
                actions.append(
                    IntendedAction(
                        ModuleName.FAN, Intent.TURN_OFF_FAN, "vacant_or_cool", "fan", {"temperature": temperature}
                    )
                )

        if statuses[ModuleName.CLIMATE].ready and temperature is not None:
            ac_type = data.get(CONF_AC_CONTROL_TYPE, ACControlType.NONE)
            if occupied and not door_open_long_enough and temperature >= float(options[CONF_CLIMATE_ON_TEMP]):
                intent = Intent.SEND_IR_POWER_ON if ac_type == ACControlType.IR_SCRIPTS else Intent.TURN_ON_CLIMATE
                actions.append(
                    IntendedAction(
                        ModuleName.CLIMATE,
                        intent,
                        "occupied_hot_and_door_allowed",
                        "climate",
                        {"temperature": temperature},
                    )
                )
            elif vacant_long_enough or door_open_long_enough or temperature <= float(options[CONF_CLIMATE_OFF_TEMP]):
                intent = Intent.SEND_IR_POWER_OFF if ac_type == ACControlType.IR_SCRIPTS else Intent.TURN_OFF_CLIMATE
                actions.append(
                    IntendedAction(
                        ModuleName.CLIMATE, intent, "vacant_door_open_or_cool", "climate", {"temperature": temperature}
                    )
                )

        if actions:
            summary = ", ".join(action.intent.value for action in actions)
            reason = ", ".join(dict.fromkeys(action.reason for action in actions))
        else:
            summary = Intent.NONE.value
            reason = "no_rule_matched_or_module_not_ready"
        return DryRunDecision(now, occupied, temperature, illuminance, door_open, tuple(actions), summary, reason)
