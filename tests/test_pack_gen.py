from __future__ import annotations

from pathlib import Path

from urisys.managers.markpact_manager import MarkpactManager
from urisys.managers.markpact_pack_gen import generate_pack_markpact, package_schemes
from urisys.managers.markpact_run import run_markpact

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent
STEPPER_PKG = TELLMESH / "uristepper" / "uristepper"


def test_generate_embeds_full_source(tmp_path):
    text = generate_pack_markpact(STEPPER_PKG)
    out = tmp_path / "uristepper.markpact.md"
    out.write_text(text, encoding="utf-8")

    # every .py of the package is embedded as a markpact:module block
    assert "markpact:module path=uristepper/handlers.py" in text
    assert "markpact:module path=uristepper/drivers/mock.py" in text
    assert "markpact:run" in text

    info = MarkpactManager().validate(out)
    assert info["ok"] is True
    assert info["scheme"] == "stepper"


def test_unpack_and_execute_embedded_handler(tmp_path):
    """The generated markpact must unpack into .markpact-style dir and its
    python:// handler must execute from the embedded code (no installed pkg)."""
    text = generate_pack_markpact(STEPPER_PKG)
    src = tmp_path / "uristepper.markpact.md"
    src.write_text(text, encoding="utf-8")

    result = run_markpact(src, mode="pack", out=tmp_path / ".markpact")
    assert result["ok"] is True
    patterns = {r["pattern"] for r in result["routes"]}
    assert "stepper://{device}/axis/{axis}/query/status" in patterns

    # compile + call proves the embedded handler module runs
    compiled = MarkpactManager(cache_root=tmp_path / ".markpact").compile(src, force=True)
    assert "uristepper/handlers.py" in compiled.module_files

    # isolate from other tests that unpack a same-named 'uristepper' package:
    # force resolution to THIS unpack dir.
    import sys

    for name in [m for m in sys.modules if m == "uristepper" or m.startswith("uristepper.")]:
        del sys.modules[name]
    sys.path.insert(0, str(compiled.cache_dir))

    from urisysedge.manifest import register_manifest_file
    from urisysedge.runtime import Runtime

    rt = Runtime(events_path=str(tmp_path / "ev.jsonl"),
                 config={"device_profile": {"axes": {"x": {"steps_per_rev": 200}}, "safety": {"x": {}}}})
    register_manifest_file(rt, compiled.manifest_path)
    res = rt.call("stepper://m1/axis/x/query/status", {}, {})
    assert res["ok"] is True
    assert res["result"]["driver"] == "mock"


def test_multi_scheme_requires_scheme_selection():
    manifest = {"id": "x", "schemes": ["kv", "log"], "uri_patterns": []}
    assert package_schemes(manifest) == ["kv", "log"]


def test_run_modes_interface_and_adapter(tmp_path):
    text = generate_pack_markpact(STEPPER_PKG)
    src = tmp_path / "uristepper.markpact.md"
    src.write_text(text, encoding="utf-8")

    iface = run_markpact(src, mode="interface", out=tmp_path / ".markpact")
    assert iface["ok"] and iface["scheme"] == "stepper"
    assert len(iface["interface"]) == 7

    adapter = run_markpact(src, mode="adapter", out=tmp_path / ".markpact")
    assert adapter["ok"] and adapter["wire"]
