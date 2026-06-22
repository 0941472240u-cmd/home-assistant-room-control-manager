from __future__ import annotations

from custom_components.room_control_manager.diagnostics import _redact_mapping


def test_diagnostics_redacts_names_areas_and_entity_ids() -> None:
    redacted = _redact_mapping(
        {
            "room_name": "Private room name",
            "area_id": "private_area",
            "presence_primary": "binary_sensor.generic_presence",
            "temperature_sensors": ["sensor.generic_temperature"],
            "dry_run": True,
        }
    )
    assert redacted["room_name"] == "<redacted>"
    assert redacted["area_id"] == "<redacted>"
    assert redacted["presence_primary"].startswith("entity-")
    assert redacted["temperature_sensors"][0].startswith("entity-")
    assert redacted["dry_run"] is True
