"""Execute compact *.uri.flow.yaml documents step-by-step through the lab gateway."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    raise ValueError(f"after/depends_on must be string or list, got {type(value).__name__}")


def _parse_step(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        return {"id": None, "uri": raw, "payload": {}, "after": [], "operation": None, "kind": None}
    if isinstance(raw, dict):
        if "uri" not in raw and len(raw) == 1:
            uri, payload = next(iter(raw.items()))
            return {
                "id": None,
                "uri": str(uri),
                "payload": dict(payload or {}),
                "after": [],
                "operation": None,
                "kind": None,
            }
        if "uri" not in raw:
            raise ValueError("step mapping must contain 'uri' or be a single URI mapping")
        payload = raw.get("with", raw.get("payload", {})) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"payload for {raw.get('uri')} must be a mapping")
        return {
            "id": raw.get("id"),
            "uri": str(raw["uri"]),
            "payload": payload,
            "after": _as_list(raw.get("after", raw.get("depends_on"))),
            "operation": raw.get("operation"),
            "kind": raw.get("kind"),
        }
    raise ValueError(f"unsupported step type: {type(raw).__name__}")


def _load_flow_document(path: str | Path) -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("flow document must be a YAML mapping")
    flow_meta = data.get("flow") or {}
    if not isinstance(flow_meta, dict):
        flow_meta = {}
    steps_raw = data.get("do") or data.get("steps")
    if not isinstance(steps_raw, list) or not steps_raw:
        raise ValueError("flow must contain non-empty 'do' or 'steps' list")
    steps = [_parse_step(item) for item in steps_raw]
    return {
        "flow_id": str(flow_meta.get("id") or Path(path).stem.replace(".uri.flow", "")),
        "description": flow_meta.get("description"),
        "defaults": dict(data.get("defaults") or {}),
        "steps": steps,
    }


def _node_id(step: dict[str, Any], used: set[str]) -> str:
    if step.get("id"):
        return str(step["id"])
    uri = str(step["uri"])
    base = uri.split("://", 1)[-1].replace("/", "_").replace("{", "").replace("}", "")
    node_id = base or "step"
    idx = 2
    while node_id in used:
        node_id = f"{base}_{idx}"
        idx += 1
    used.add(node_id)
    return node_id


def _expand_graph(doc: dict[str, Any]) -> dict[str, Any]:
    used: set[str] = set()
    nodes: list[dict[str, Any]] = []
    previous_id: str | None = None
    for step in doc["steps"]:
        node_id = _node_id(step, used)
        depends_on = step["after"] or ([previous_id] if previous_id else [])
        nodes.append(
            {
                "id": node_id,
                "uri": step["uri"],
                "payload": step.get("payload") or {},
                "operation": step.get("operation"),
                "kind": step.get("kind"),
                "depends_on": depends_on,
            }
        )
        previous_id = node_id
    edges = [{"from": dep, "to": node["id"], "type": "depends_on"} for node in nodes for dep in node.get("depends_on") or []]
    return {
        "nl2uri": {"version": 1, "kind": "workflow_graph", "source": "compact_uri_flow"},
        "graph": {
            "id": doc["flow_id"],
            "version": 1,
            "kind": "workflow",
            "description": doc.get("description"),
            "nodes": nodes,
            "edges": edges,
        },
    }


def _topo_sort(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {node["id"]: node for node in nodes}
    indegree = {node["id"]: 0 for node in nodes}
    edges: dict[str, list[str]] = {node["id"]: [] for node in nodes}
    for node in nodes:
        for dep in node.get("depends_on") or []:
            if dep not in by_id:
                continue
            indegree[node["id"]] += 1
            edges[dep].append(node["id"])
    ready = [node_id for node_id, deg in indegree.items() if deg == 0]
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for nxt in edges[current]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
    if len(order) != len(nodes):
        return nodes
    return [by_id[node_id] for node_id in order]


def plan_flow(flow_path: str | Path) -> dict[str, Any]:
    doc = _load_flow_document(flow_path)
    expanded = _expand_graph(doc)
    nodes = _topo_sort(expanded["graph"]["nodes"])
    return {
        "flow_id": doc["flow_id"],
        "description": doc.get("description"),
        "defaults": doc.get("defaults") or {},
        "flow_path": str(flow_path),
        "graph": expanded,
        "steps": nodes,
    }


def _step_ok(response: dict[str, Any], *, allow_real: bool) -> bool:
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


def run_flow_file(
    flow_path: str | Path,
    *,
    call_uri: Callable[[str, dict[str, Any], dict[str, Any]], dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    plan = plan_flow(flow_path)
    ctx = dict(context or {})
    ctx.setdefault("approved", True)
    defaults = plan.get("defaults") or {}
    if defaults.get("approved") is not None:
        ctx.setdefault("approved", bool(defaults.get("approved")))
    if defaults.get("dry_run") is not None and "dry_run" not in ctx:
        ctx["dry_run"] = bool(defaults.get("dry_run"))

    results: list[dict[str, Any]] = []
    for node in plan["steps"]:
        uri = str(node["uri"])
        payload = dict(node.get("payload") or {})
        step_ctx = dict(ctx)
        if uri.startswith("chat://") and "execute" in uri:
            payload.setdefault("approved", True)
            payload["dry_run"] = False
            step_ctx["dry_run"] = False
            step_ctx["allow_real"] = True
        try:
            response = call_uri(uri, payload, step_ctx)
        except Exception as exc:
            response = {"ok": False, "uri": uri, "error": str(exc)}
        step_ok = _step_ok(response, allow_real=bool(step_ctx.get("allow_real")))
        results.append(
            {
                "id": node.get("id"),
                "uri": uri,
                "operation": node.get("operation"),
                "kind": node.get("kind"),
                "depends_on": node.get("depends_on") or [],
                "payload": payload,
                "context": {k: step_ctx[k] for k in ("approved", "allow_real", "dry_run", "display", "xauthority") if k in step_ctx},
                "ok": step_ok,
                "response": response,
            }
        )
        if not step_ok:
            break
    return {
        "flow_id": plan["flow_id"],
        "flow_path": plan["flow_path"],
        "description": plan["description"],
        "graph": plan["graph"],
        "ok": all(step["ok"] for step in results) and bool(results),
        "steps": results,
    }
