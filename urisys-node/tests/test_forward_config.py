from __future__ import annotations

import json
import os
from unittest import mock

import urisysnode.forward_config as fc
from urisysedge.runtime import Runtime
from urisysnode.serve import build_runtime


def _runtime(tmp_path) -> Runtime:
    rt = Runtime(events_path=str(tmp_path / "events.jsonl"))
    rt._loaded_packs = set()
    return rt


def test_load_forward_entries_from_config():
    config = {
        "forwards": [
            {
                "scheme": "imgl",
                "endpoint": "http://127.0.0.1:8219",
                "patterns": ["imgl://{host}/image/latest/query/layout"],
            }
        ]
    }
    entries = fc.load_forward_entries(config=config)
    assert len(entries) == 1
    assert entries[0]["scheme"] == "imgl"


def test_load_forward_entries_env_inline():
    payload = json.dumps([
        {
            "scheme": "vql",
            "endpoint": "http://127.0.0.1:8220",
            "patterns": ["vql://{host}/ui/latest/query/compare"],
        }
    ])
    with mock.patch.dict(os.environ, {"URISYS_NODE_FORWARDS": payload}, clear=False):
        entries = fc.load_forward_entries()
    assert entries[0]["scheme"] == "vql"


def test_wire_forward_packs_registers_routes(tmp_path):
    rt = _runtime(tmp_path)
    results = fc.wire_forward_packs(
        rt,
        [{
            "scheme": "imgl",
            "endpoint": "http://127.0.0.1:8219",
            "patterns": ["imgl://{host}/image/latest/query/layout"],
        }],
    )
    assert results[0]["ok"] is True
    assert "imgl" in rt._loaded_packs
    assert any(r.pattern.startswith("imgl://") for r in rt.routes)


def test_command_register_forward(tmp_path):
    rt = _runtime(tmp_path)
    import urisysnode.handlers as handlers

    out = handlers.command_register_forward(
        {
            "scheme": "vql",
            "endpoint": "http://127.0.0.1:8220",
            "patterns": ["vql://{host}/ui/latest/query/detect"],
        },
        {"approved": True, "runtime": rt},
    )
    assert out["ok"] is True
    assert "vql" in rt._loaded_packs


def test_build_runtime_wires_config_forwards(tmp_path, monkeypatch):
    config_path = tmp_path / "profile.json"
    config_path.write_text(
        json.dumps({
            "forwards": [{
                "scheme": "imgl",
                "endpoint": "http://127.0.0.1:8219",
                "patterns": ["imgl://{host}/image/latest/query/layout"],
            }],
        }),
        encoding="utf-8",
    )
    monkeypatch.setenv("URISYS_NODE_CONFIG", str(config_path))
    monkeypatch.setenv("URISYS_NODE_PACKS", "node")
    rt = build_runtime(str(config_path))
    assert any(r.pattern.startswith("imgl://") for r in rt.routes)
