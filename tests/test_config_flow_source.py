from __future__ import annotations

from pathlib import Path

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "room_control_manager"


def test_options_uses_single_reload_framework() -> None:
    source = (COMPONENT / "options_flow.py").read_text()
    assert "OptionsFlowWithReload" in source
    assert "async_reload" not in source
    assert "add_update_listener" not in source


def test_reconfigure_uses_update_reload_and_abort() -> None:
    source = (COMPONENT / "config_flow.py").read_text()
    assert "async_step_reconfigure" in source
    assert "async_update_reload_and_abort" in source


def test_entity_ids_are_selector_inputs_not_constants() -> None:
    source = (COMPONENT / "const.py").read_text()
    assert "binary_sensor." not in source
    assert "sensor." not in source
    assert "light." not in source
    assert "script." not in source
