"""Set repository URLs and the manifest code owner before the first GitHub push."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "custom_components" / "room_control_manager" / "manifest.json"
REPOSITORY_NAME = "home-assistant-room-control-manager"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update manifest metadata for the GitHub account that will host the repository."
    )
    parser.add_argument("owner", help="GitHub username or organization name")
    args = parser.parse_args()
    owner = args.owner.strip().lstrip("@")
    if not owner or "/" in owner or " " in owner:
        raise SystemExit("Enter one valid GitHub username or organization name.")

    repository_url = f"https://github.com/{owner}/{REPOSITORY_NAME}"
    manifest = json.loads(MANIFEST.read_text())
    manifest["documentation"] = repository_url
    manifest["issue_tracker"] = f"{repository_url}/issues"
    manifest["codeowners"] = [f"@{owner}"]
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Updated manifest metadata for {repository_url}")


if __name__ == "__main__":
    main()
