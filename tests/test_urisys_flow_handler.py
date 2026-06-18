"""Integration: capability with ``urisys://flow/`` handler delegates to markpact:flow."""

from __future__ import annotations

from pathlib import Path

import yaml

from urisys.managers.markpact_manager import MarkpactManager

PROCESS_FLOW_MARKPACT = """\
# UriPack: process-flow demo

```yaml markpact:pack
apiVersion: urisys.io/v1
kind: UriPack
metadata:
  id: process-flow-demo
  version: 0.1.0
schemes: [process]
capabilities:
  - id: process.ping
    uri: process://local/query/ping
    kind: query
    operation: ping
    handler: markpact://self/python/ping
    approval: not_required
  - id: process.run_cycle
    uri: process://machine-cycle/command/run
    kind: command
    operation: run
    handler: urisys://flow/machine-cycle
    approval: not_required
    side_effects: false
```

```python markpact:handler id=ping
def handle(payload, context):
    return {"stage": "ping", "value": payload.get("n", 0)}
```

```yaml markpact:flow id=machine-cycle
defaults:
  approved: true
do:
  - process://local/query/ping:
      n: 1
```
"""


def test_process_capability_runs_embedded_flow_via_urisys_handler(tmp_path):
    src = tmp_path / "demo.markpact.md"
    src.write_text(PROCESS_FLOW_MARKPACT, encoding="utf-8")

    compiled = MarkpactManager(cache_root=tmp_path / ".markpact").compile(src, force=True)
    manifest = yaml.safe_load(compiled.manifest_path.read_text(encoding="utf-8"))

    assert manifest["handlers"]["urisys"]["run"] == "urisys://flow/machine-cycle"
    assert "machine-cycle" in manifest["urisys"]["flows"]

    from urisysedge.manifest import register_manifest_file
    from urisysedge.runtime import Runtime

    rt = Runtime(events_path=str(tmp_path / "events.jsonl"), config={})
    register_manifest_file(rt, compiled.manifest_path)

    res = rt.call("process://machine-cycle/command/run", {}, {"approved": True})
    assert res["ok"] is True
    assert res["result"]["flow_id"] == "machine-cycle"
    assert res["result"]["steps"][0]["result"]["stage"] == "ping"
