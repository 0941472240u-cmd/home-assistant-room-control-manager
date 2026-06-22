from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "room_control_manager"


def test_manifest_identity() -> None:
    manifest = json.loads((COMPONENT / "manifest.json").read_text())
    assert manifest["domain"] == "room_control_manager"
    assert manifest["version"] == "0.1.0"
    assert manifest["config_flow"] is True
    assert "single_config_entry" not in manifest


def test_hacs_minimum_version() -> None:
    hacs = json.loads((ROOT / "hacs.json").read_text())
    assert hacs["homeassistant"] == "2026.3.0"


def test_only_one_custom_integration() -> None:
    assert [path.name for path in (ROOT / "custom_components").iterdir() if path.is_dir()] == ["room_control_manager"]


def test_translation_files_are_complete_json() -> None:
    for name in ("strings.json", "translations/en.json", "translations/th.json"):
        data = json.loads((COMPONENT / name).read_text())
        assert "config" in data
        assert "options" in data
        assert "issues" in data
        assert "entity" in data
