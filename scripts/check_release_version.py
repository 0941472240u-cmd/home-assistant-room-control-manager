"""Check a Git tag against manifest version."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "custom_components/room_control_manager/manifest.json").read_text())
tag = sys.argv[1] if len(sys.argv) > 1 else "v0.1.0"
if tag.removeprefix("v") != manifest["version"]:
    raise SystemExit(f"Tag {tag} does not match manifest version {manifest['version']}")
print(f"Release version {tag} is consistent")
