"""UriProcess conformance — dry-run matrix for reference process Markpacts."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from urisys.managers.markpact_run import run_markpact

TELLMESH = Path(__file__).resolve().parents[2]
RESOLVER = TELLMESH / "markpact-contracts" / "packs" / "examples" / "urisys.runtime.resolver.yaml"

PROCESS_FLOWS = [
    ("machine-cycle-process.markpact.md", "machine-cycle", {}),
    ("desktop-automation-processes.markpact.md", "gui-open-software-center", {}),
    ("desktop-automation-processes.markpact.md", "rdp-kvm-smoke", {}),
    (
        "desktop-automation-processes.markpact.md",
        "install-update-verify-browser",
        {"URISYS_RESOLVER_CONFIG": str(RESOLVER)},
    ),
]


@pytest.mark.parametrize("markpact_file,flow_id,extra_env", PROCESS_FLOWS)
@pytest.mark.skipif(not os.environ.get("TELLMESH_ROOT"), reason="needs TELLMESH_ROOT")
def test_process_flow_conformance_dry_run(
    markpact_file: str,
    flow_id: str,
    extra_env: dict[str, str],
    tmp_path,
    monkeypatch,
):
    path = TELLMESH / "markpact-contracts" / "packs" / markpact_file
    if not path.is_file():
        pytest.skip(f"{markpact_file} missing")

    monkeypatch.setenv("TELLMESH_ROOT", os.environ["TELLMESH_ROOT"])
    for key, value in extra_env.items():
        monkeypatch.setenv(key, value)

    result = run_markpact(
        path,
        mode="flow",
        out=tmp_path / f"{flow_id}-out",
        approve=True,
        dry_run=True,
        flow_id=flow_id,
    )
    assert result["ok"] is True, result
