from __future__ import annotations

import hashlib
import json
import os
import secrets
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _data_dir() -> Path:
    root = Path(os.environ.get("URISYS_NODE_DATA", "data"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _identity_path() -> Path:
    return _data_dir() / "node-identity.json"


def _pairing_path() -> Path:
    return _data_dir() / "node-pairing.json"


def _hostname() -> str:
    return socket.gethostname()


def load_identity() -> dict[str, Any]:
    path = _identity_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    node_id = os.environ.get("URISYS_NODE_ID") or _hostname()
    identity = {
        "node_id": node_id,
        "hostname": _hostname(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "public_key": secrets.token_hex(16),
    }
    identity["fingerprint"] = hashlib.sha256(identity["public_key"].encode()).hexdigest()[:16]
    save_identity(identity)
    return identity


def save_identity(data: dict[str, Any]) -> None:
    _identity_path().write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_pairing() -> dict[str, Any]:
    path = _pairing_path()
    if not path.exists():
        return {"paired": False}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"paired": False}


def enroll(controller: str, code: str | None = None, token: str | None = None) -> dict[str, Any]:
    identity = load_identity()
    pairing = {
        "paired": True,
        "controller": controller,
        "enrolled_at": datetime.now(timezone.utc).isoformat(),
        "pair_code": code,
        "token_prefix": (token or "")[:8] or None,
        "node_id": identity["node_id"],
        "capabilities": ["screen", "kvm", "him", "ocr", "llm", "process", "service"],
    }
    _pairing_path().write_text(json.dumps(pairing, indent=2), encoding="utf-8")
    return pairing


def save_pairing(data: dict[str, Any]) -> None:
    _pairing_path().write_text(json.dumps(data, indent=2), encoding="utf-8")


def set_remote_control(active: bool, message: str | None = None) -> dict[str, Any]:
    pairing = load_pairing()
    pairing["remote_control_active"] = active
    if message is not None:
        pairing["indicator_message"] = message
    save_pairing(pairing)
    return pairing


def require_paired(context: dict[str, Any]) -> None:
    if os.environ.get("URISYS_NODE_SKIP_PAIRING") == "1":
        return
    if context.get("skip_pairing"):
        return
    if not load_pairing().get("paired"):
        raise PermissionError("node is not paired — run: urisys-node enroll --controller …")


def health_payload(version: str = "0.1.0") -> dict[str, Any]:
    identity = load_identity()
    pairing = load_pairing()
    return {
        "ok": True,
        "service": "urisys-node",
        "node_id": identity["node_id"],
        "fingerprint": identity.get("fingerprint"),
        "version": version,
        "paired": bool(pairing.get("paired")),
        "controller": pairing.get("controller"),
        "remote_control_active": bool((pairing.get("remote_control_active"))),
    }
