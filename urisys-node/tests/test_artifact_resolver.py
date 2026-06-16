from __future__ import annotations

import json
from pathlib import Path

import yaml

from urisysnode.artifact_resolver import load_artifact_index, load_node_profile, select_artifact


def test_select_artifact_by_platform(tmp_path: Path) -> None:
    index = {
        "artifacts": [
            {"target": "linux-arm64", "platform": "linux/arm64", "ref": "img:arm"},
            {"target": "linux-amd64-mock", "platform": "linux/amd64", "ref": "img:amd64", "runtime": "docker", "capabilities": ["mock-stepper"]},
        ]
    }
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(
        yaml.safe_dump({"node": {"platform": "linux/amd64", "runtimes": ["docker"], "capabilities": ["mock-stepper"]}}),
        encoding="utf-8",
    )
    art = select_artifact(index, load_node_profile(profile_path))
    assert art["ref"] == "img:amd64"


def test_load_artifact_index(tmp_path: Path) -> None:
    p = tmp_path / "index.json"
    p.write_text(json.dumps({"schema": "markpact.artifact-index.v1", "artifacts": []}), encoding="utf-8")
    assert load_artifact_index(p)["schema"] == "markpact.artifact-index.v1"
