from __future__ import annotations

import ast
from pathlib import Path

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "room_control_manager"
FORBIDDEN_ATTRIBUTES = {"async_call", "call"}
FORBIDDEN_SERVICE_TEXT = {
    "light.turn_on",
    "light.turn_off",
    "fan.turn_on",
    "fan.turn_off",
    "climate.turn_on",
    "climate.turn_off",
    "script.turn_on",
    "switch.turn_on",
    "switch.turn_off",
}


def test_source_contains_no_service_calls() -> None:
    for path in COMPONENT.rglob("*.py"):
        source = path.read_text()
        for token in FORBIDDEN_SERVICE_TEXT:
            assert token not in source, f"Forbidden service token {token} in {path}"
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES:
                if isinstance(node.value, ast.Attribute) and node.value.attr == "services":
                    raise AssertionError(f"Home Assistant service call found in {path}:{node.lineno}")
