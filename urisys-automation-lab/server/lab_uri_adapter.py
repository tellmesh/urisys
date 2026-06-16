"""Lab HTTP adapter for uri3 — routes workflow steps through automation-lab call_uri."""

from __future__ import annotations

from typing import Any, Callable

from uri3.graph.execution_models import ExecutionContext
from uri3.graph.models import GraphNode

# Schemes handled locally or forwarded to urirdp via lab gateway.
LAB_SCHEMES = frozenset(
    {
        "shell",
        "browser",
        "kvm",
        "him",
        "ocr",
        "llm",
        "rdp",
        "env",
        "stt",
        "chat",
        "webrtc",
        "http",
        "https",
    }
)


def step_ok(response: dict[str, Any], *, allow_real: bool) -> bool:
    if not bool(response.get("ok")):
        return False
    result = response.get("result") if isinstance(response.get("result"), dict) else {}
    if isinstance(result, dict):
        if result.get("ok") is False:
            return False
        exit_code = result.get("exit_code")
        if exit_code is not None and exit_code != 0:
            return False
        if allow_real and result.get("mode") == "dry_run":
            return False
    return True


class LabCallAdapter:
    schemes = LAB_SCHEMES

    def execute(self, node: GraphNode, context: ExecutionContext) -> dict[str, Any]:
        call_uri: Callable[[str, dict[str, Any], dict[str, Any]], dict[str, Any]] | None = (
            context.adapter_state.get("call_uri")
        )
        if call_uri is None:
            return {"ok": False, "error": "lab call_uri not configured"}

        base_ctx = dict(context.adapter_state.get("lab_context") or {})
        uri = str(node.uri)
        payload = dict(node.payload or {})
        step_ctx = dict(base_ctx)

        if uri.startswith("chat://") and "execute" in uri:
            payload.setdefault("approved", True)
            payload["dry_run"] = False
            step_ctx["dry_run"] = False
            step_ctx["allow_real"] = True

        if context.dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "uri": uri,
                "operation": node.operation,
                "payload": payload,
            }

        try:
            response = call_uri(uri, payload, step_ctx)
        except Exception as exc:
            response = {"ok": False, "uri": uri, "error": str(exc)}

        ok = step_ok(response, allow_real=bool(step_ctx.get("allow_real")))
        return {
            "ok": ok,
            "uri": uri,
            "operation": node.operation,
            "response": response,
        }
