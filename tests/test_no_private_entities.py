from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    "0x" + "a4c" + "138",
    "input_boolean" + ".room_",
    "input_number" + ".room_",
    "script" + ".air_",
    "binary_sensor" + ".0x",
)


def test_no_known_private_entity_ids() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix in {".png", ".zip", ".pyc"}:
            continue
        text = path.read_text(errors="ignore")
        for value in FORBIDDEN:
            assert value not in text, f"Private entity pattern found in {path}"
