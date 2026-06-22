from __future__ import annotations

from custom_components.room_control_manager.configuration.defaults import build_default_options
from custom_components.room_control_manager.configuration.schemas import (
    actuators_schema,
    binary_options_schema,
    climate_schema,
    ir_schema,
    modules_options_schema,
    numeric_options_schema,
    options_review_schema,
    review_schema,
    room_schema,
    sensors_schema,
    thresholds_options_schema,
)


def test_every_flow_schema_builds() -> None:
    options = build_default_options()
    schemas = (
        room_schema({}),
        sensors_schema({}),
        actuators_schema({}),
        climate_schema({}),
        ir_schema({}),
        review_schema(),
        modules_options_schema(options),
        binary_options_schema(options, {}),
        numeric_options_schema(options, {}),
        thresholds_options_schema(options),
        options_review_schema(),
    )
    assert all(schema is not None for schema in schemas)
