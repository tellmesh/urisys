from __future__ import annotations

from typing import Any

from urisysnode.identity import load_pairing, require_paired, set_remote_control


def query_health(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    del payload, context
    from urisysnode.identity import health_payload

    return health_payload()


def query_identity(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    del payload, context
    from urisysnode.identity import load_identity

    identity = load_identity()
    pairing = load_pairing()
    return {
        "node_id": identity["node_id"],
        "fingerprint": identity.get("fingerprint"),
        "hostname": identity.get("hostname"),
        "paired": bool(pairing.get("paired")),
        "controller": pairing.get("controller"),
        "capabilities": pairing.get("capabilities") or ["screen", "kvm", "him"],
    }


def command_indicator_on(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    require_paired(context)
    pairing = set_remote_control(True, payload.get("message", "Urisys remote control active"))
    return {"remote_control_active": True, "message": pairing.get("indicator_message")}


def command_indicator_off(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    del payload
    require_paired(context)
    set_remote_control(False)
    return {"remote_control_active": False}
