from __future__ import annotations

from typing import Any


def ui_detect(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    target = str(payload.get("target") or payload.get("text") or payload.get("selector") or "")
    boxes = (context.get("state", {}).get("latest_ocr") or {}).get("boxes") or payload.get("boxes") or []
    matches = []
    for box in boxes:
        text = str(box.get("text") or "")
        if not target or target.lower() in text.lower():
            matches.append(box)
    return {
        "target": target,
        "matches": matches[:20],
        "count": len(matches),
        "source": "urivql-mock",
    }


def ui_compare(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    before = payload.get("before") or context.get("state", {}).get("screen_before")
    after = payload.get("after") or context.get("state", {}).get("screen_after")
    expect = payload.get("expect") or {}
    changed = before != after if before is not None and after is not None else bool(expect.get("changed", True))
    ok = changed if expect.get("changed") is None else (changed == bool(expect.get("changed")))
    return {
        "ok": ok,
        "changed": changed,
        "expect": expect,
        "source": "urivql-mock",
    }
