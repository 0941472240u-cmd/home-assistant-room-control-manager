"""Static validation used locally and by GitHub Actions."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "room_control_manager"
REQUIRED_FILES = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "CHANGELOG.md",
    ROOT / "hacs.json",
    ROOT / ".github" / "workflows" / "validate-hacs.yml",
    ROOT / ".github" / "workflows" / "hassfest.yml",
    ROOT / ".github" / "workflows" / "tests.yml",
    ROOT / ".github" / "workflows" / "release.yml",
    INTEGRATION / "__init__.py",
    INTEGRATION / "manifest.json",
    INTEGRATION / "config_flow.py",
    INTEGRATION / "options_flow.py",
    INTEGRATION / "diagnostics.py",
    INTEGRATION / "repairs.py",
    INTEGRATION / "sensor.py",
    INTEGRATION / "binary_sensor.py",
    INTEGRATION / "strings.json",
    INTEGRATION / "translations" / "en.json",
    INTEGRATION / "translations" / "th.json",
)

missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
if missing:
    raise SystemExit(f"Missing required files: {missing}")

manifest = json.loads((INTEGRATION / "manifest.json").read_text())
if (
    manifest.get("domain") != "room_control_manager"
    or manifest.get("version") != "0.1.0"
    or manifest.get("config_flow") is not True
):
    raise SystemExit("Manifest identity or version is invalid")
if "single_config_entry" in manifest:
    raise SystemExit("single_config_entry must not be present")

hacs = json.loads((ROOT / "hacs.json").read_text())
if hacs.get("homeassistant") != "2026.3.0":
    raise SystemExit("hacs.json must declare Home Assistant 2026.3.0")

components = sorted(path.name for path in (ROOT / "custom_components").iterdir() if path.is_dir())
if components != ["room_control_manager"]:
    raise SystemExit(f"Repository must contain exactly one integration: {components}")

for path in ROOT.rglob("*.json"):
    json.loads(path.read_text())
for path in (*INTEGRATION.rglob("*.py"), *ROOT.joinpath("scripts").rglob("*.py")):
    ast.parse(path.read_text(), filename=str(path))

for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix in {".png", ".pyc", ".zip"}:
        continue
    text = path.read_text(errors="ignore")
    marker = "TO" + "DO"
    if marker in text:
        raise SystemExit(f"Unresolved work marker found in {path.relative_to(ROOT)}")

print("Repository static validation passed")
