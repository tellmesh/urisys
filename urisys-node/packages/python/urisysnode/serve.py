from __future__ import annotations

import importlib
import json
import os
import sys
import warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .identity import health_payload, load_identity
from .runtime import Runtime, load_json

# pack alias -> module exposing register(runtime). `node` is the package's own
# routes (always present); the rest are optional hardware/AI capability packs.
PACK_MODULES: dict[str, str] = {
    "node": "urisysnode.routes",
    "screen": "uriscreen.routes",
    "kvm": "urikvm",
    "him": "urihim",
    "ocr": "uriocr",
    "llm": "urillm",
}
CORE_PACKS = {"node"}


def _extend_pack_paths() -> None:
    root = Path(__file__).resolve().parents[3]
    for rel in ("../urikvm-docker/packages/python", "../urirdp-docker/packages/python"):
        path = (root / rel).resolve()
        if path.is_dir() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


def _register_pack(rt: Runtime, pack: str) -> bool:
    """Import and register one capability pack. Optional packs that are not
    installed are skipped with a warning so the node still serves the rest."""
    module_name = PACK_MODULES.get(pack)
    if module_name is None:
        warnings.warn(f"Unknown urisys-node pack '{pack}' — skipping.", stacklevel=2)
        return False
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        top = module_name.split(".", 1)[0]
        # A missing dependency *of* an installed pack must not be swallowed.
        if exc.name not in (module_name, top):
            raise
        if pack in CORE_PACKS:
            raise
        warnings.warn(
            f"Skipping urisys-node pack '{pack}': module '{module_name}' is not "
            f"installed (pip install {top}).",
            stacklevel=2,
        )
        return False
    module.register(rt)
    return True


def build_runtime(config_path: str | None = None) -> Runtime:
    _extend_pack_paths()
    from urisysnode.env import load_urisys_env

    load_urisys_env()
    config_file = config_path or os.environ.get("URISYS_NODE_CONFIG", "config/node-profile.json")
    config = load_json(config_file) if Path(config_file).exists() else {}
    rt = Runtime(events_path=os.environ.get("URISYS_NODE_EVENTS", "data/events.jsonl"), config=config)

    packs = os.environ.get("URISYS_NODE_PACKS", "node,screen,kvm,him,ocr,llm").split(",")
    packs = [p.strip() for p in packs if p.strip()]

    rt._loaded_packs = set()  # type: ignore[attr-defined]
    for pack in packs:
        if _register_pack(rt, pack):
            rt._loaded_packs.add(pack)  # type: ignore[attr-defined]

    return rt


def load_pack_into_runtime(runtime: Runtime, pack: str) -> dict[str, Any]:
    """Hot-load an installed capability pack into a live runtime, so an already
    deployed node can gain new URI handlers over the wire without a restart.
    Idempotent: re-loading an active pack is a no-op (no duplicate routes)."""
    pack = (pack or "").strip()
    if not pack:
        return {"ok": False, "error": "pack name is required"}
    loaded = getattr(runtime, "_loaded_packs", None)
    if loaded is None:
        loaded = set()
        runtime._loaded_packs = loaded  # type: ignore[attr-defined]
    if pack in loaded:
        return {"ok": True, "pack": pack, "loaded": True, "already_loaded": True, "new_routes": []}
    before = {r.pattern for r in runtime.routes}
    try:
        ok = _register_pack(runtime, pack)
    except ModuleNotFoundError as exc:
        return {"ok": False, "pack": pack, "loaded": False, "error": str(exc)}
    if ok:
        loaded.add(pack)
    new_routes = sorted({r.pattern for r in runtime.routes} - before)
    return {"ok": bool(ok), "pack": pack, "loaded": bool(ok), "new_routes": new_routes}


def register_forward_pack(
    runtime: Runtime,
    scheme: str,
    endpoint: str,
    patterns: list[str],
) -> dict[str, Any]:
    """Make a capability served by an out-of-process worker available on this
    node: route each of the contract's declared URI patterns to a forwarding
    handler that calls the worker at ``endpoint``. This is how an artifact
    resolved from a markpact.com release (OCI image on GitHub) is wired in."""
    scheme = (scheme or "").strip()
    endpoint = (endpoint or "").strip()
    if not scheme or not endpoint:
        return {"ok": False, "error": "scheme and endpoint are required"}
    if not patterns:
        return {"ok": False, "error": "at least one uri pattern is required"}
    loaded = getattr(runtime, "_loaded_packs", None)
    if loaded is None:
        loaded = set()
        runtime._loaded_packs = loaded  # type: ignore[attr-defined]
    runtime.config.setdefault("forward_targets", {})[scheme] = endpoint
    before = {r.pattern for r in runtime.routes}
    for pattern in patterns:
        if pattern in before:
            continue
        kind = "command" if "/command/" in pattern else "query"
        runtime.register(
            pattern,
            "python://urisysnode.forward:forward_call",
            kind=kind,
            operation="forward",
            approval="required" if kind == "command" else "not_required",
            side_effects=kind == "command",
        )
    loaded.add(scheme)
    new_routes = sorted({r.pattern for r in runtime.routes} - before)
    return {"ok": True, "scheme": scheme, "endpoint": endpoint, "new_routes": new_routes}


def make_handler(runtime: Runtime):
    # Secure by default: remote capability injection is off unless explicitly
    # enabled, since loading packs grants the node new powers over the wire.
    allow_pack_load = os.environ.get("URISYS_NODE_ALLOW_PACK_LOAD", "0") == "1"

    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: int, data: dict[str, Any]) -> None:
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path == "/health":
                return self._json(200, health_payload())
            if self.path in ("/uri/routes", "/routes"):
                return self._json(200, {"ok": True, "routes": [r.pattern for r in runtime.routes]})
            if self.path.startswith("/events"):
                limit = 50
                if "limit=" in self.path:
                    try:
                        limit = int(self.path.split("limit=", 1)[1])
                    except ValueError:
                        pass
                return self._json(200, {"ok": True, "events": runtime.events.tail(limit)})
            return self._json(404, {"ok": False, "error": "not found"})

        def do_POST(self) -> None:
            if self.path == "/uri/pack":
                if not allow_pack_load:
                    return self._json(403, {
                        "ok": False,
                        "error": "pack loading disabled; start node with URISYS_NODE_ALLOW_PACK_LOAD=1",
                    })
                length = int(self.headers.get("Content-Length") or "0")
                req = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                result = load_pack_into_runtime(runtime, str(req.get("pack") or ""))
                return self._json(200 if result.get("ok") else 400, result)
            if self.path != "/uri/call":
                return self._json(404, {"ok": False, "error": "not found"})
            length = int(self.headers.get("Content-Length") or "0")
            body = self.rfile.read(length).decode("utf-8")
            req = json.loads(body or "{}")
            result = runtime.call(req.get("uri", ""), req.get("payload") or {}, req.get("context") or {})
            return self._json(200 if result.get("ok") else 400, result)

    return Handler


def serve(runtime: Runtime, host: str, port: int) -> None:
    identity = load_identity()
    server = ThreadingHTTPServer((host, port), make_handler(runtime))
    print(f"urisys-node listening on http://{host}:{port}")
    print(f"node_id={identity['node_id']} fingerprint={identity.get('fingerprint')}")
    print("endpoints: GET /health  GET /uri/routes  GET /events  POST /uri/call  POST /uri/pack")
    for route in runtime.routes:
        print(" -", route.pattern)
    server.serve_forever()
