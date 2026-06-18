"""Platform export from UriProcess Markpacts."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from urisys.managers.platform_export import (
    build_resolver_yaml,
    collect_process_uris,
    export_platform_artifacts,
)

TELLMESH = Path(__file__).resolve().parents[2]
MACHINE_CYCLE = TELLMESH / "markpact-contracts" / "packs" / "machine-cycle-process.markpact.md"
DESKTOP = TELLMESH / "markpact-contracts" / "packs" / "desktop-automation-processes.markpact.md"


@pytest.mark.skipif(not MACHINE_CYCLE.is_file(), reason="machine-cycle markpact missing")
def test_collect_process_uris_machine_cycle():
    collected = collect_process_uris(MACHINE_CYCLE)
    assert "machine-01" in collected["authorities"]
    assert "operator" in collected["authorities"]
    assert "stepper" in collected["schemes"]
    assert "machine-cycle" in collected["flow_ids"]


@pytest.mark.skipif(not DESKTOP.is_file(), reason="desktop automation markpact missing")
def test_collect_process_uris_desktop():
    collected = collect_process_uris(DESKTOP)
    assert "local" in collected["authorities"]
    assert "kvm" in collected["schemes"]
    assert len(collected["flow_ids"]) == 4


def test_build_resolver_yaml_has_v1_metadata():
    doc = build_resolver_yaml(
        platform="linux",
        authorities=["machine-01", "local"],
        schemes=["stepper", "tts"],
        package_id="test-process",
    )
    assert doc["apiVersion"] == "tellmesh.io/v1"
    assert doc["kind"] == "UriRuntimeResolver"
    assert "machine-01" in doc["targets"]


@pytest.mark.skipif(not MACHINE_CYCLE.is_file(), reason="machine-cycle markpact missing")
def test_export_platform_artifacts_writes_files(tmp_path):
    out = export_platform_artifacts(
        MACHINE_CYCLE,
        out_dir=tmp_path / "generated",
        platforms=["linux", "esp32"],
    )
    assert out["ok"] is True
    runtime = tmp_path / "generated" / "linux" / "urisys.runtime.yaml"
    assert runtime.is_file()
    data = yaml.safe_load(runtime.read_text(encoding="utf-8"))
    assert data["targets"]
    assert (tmp_path / "generated" / "esp32" / "uri_routes.h").is_file()
    assert (tmp_path / "generated" / "platform-export.json").is_file()
