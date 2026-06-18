"""Compile UriPack capabilities into runtime ``manifest.yaml``."""

from __future__ import annotations

from typing import Any

from ..managers.markpact_models import MarkpactError, scheme_from_uri
from .handlers import resolve_handler_ref
from .pack import capabilities, scheme_for_pack


def _resolve_pattern(item: dict[str, Any], *, package_id: str) -> str:
    pattern = str(item.get("pattern") or item.get("uri") or "")
    if not pattern:
        raise MarkpactError(f"Capability in {package_id!r} has no uri/pattern: {item!r}")
    return pattern


def _validate_scheme(pattern: str, *, scheme: str, package_id: str) -> None:
    item_scheme = scheme_from_uri(pattern)
    if item_scheme != scheme:
        raise MarkpactError(
            f"UriPack Markpact currently supports one scheme per file. Expected {scheme!r}, got {item_scheme!r}."
        )


def _resolve_operation(item: dict[str, Any]) -> str:
    if item.get("operation") is not None and str(item.get("operation")).strip():
        return str(item["operation"]).replace("-", "_")
    raw_id = str(item.get("id") or "")
    return raw_id.split(".")[-1].replace("-", "_") if raw_id else ""


def _resolve_kind(item: dict[str, Any], *, pattern: str) -> str:
    return str(item.get("kind") or ("command" if "/command/" in pattern else "query"))


def _build_route_dict(
    pattern: str,
    kind: str,
    operation: str,
    handler_ref: str | None,
    item: dict[str, Any],
) -> dict[str, Any]:
    route: dict[str, Any] = {
        "pattern": pattern,
        "kind": kind,
        "operation": operation,
        "side_effects": bool(item.get("side_effects", kind == "command")),
        "approval": item.get("approval", "required" if kind == "command" else "not_required"),
    }
    for key in ["command_type", "query_type", "result_type", "success_event_type", "description", "risk"]:
        if key in item:
            route[key] = item[key]
    if handler_ref:
        route["handler"] = handler_ref
    return route


def build_route(
    item: dict[str, Any],
    *,
    package_id: str,
    scheme: str,
    module_name: str,
    handlers_python: dict[str, str],
    handlers_urisys: dict[str, str],
) -> dict[str, Any]:
    pattern = _resolve_pattern(item, package_id=package_id)
    _validate_scheme(pattern, scheme=scheme, package_id=package_id)
    operation = _resolve_operation(item)
    if not operation:
        raise MarkpactError(f"Capability has no operation/id: {item!r}")
    kind = _resolve_kind(item, pattern=pattern)
    handler_ref = resolve_handler_ref(
        item.get("handler"), operation, module_name, handlers_python, handlers_urisys
    )
    return _build_route_dict(pattern, kind, operation, handler_ref, item)


def compile_manifest(
    pack: dict[str, Any],
    *,
    package_id: str,
    module_name: str,
    source_hash: str,
) -> dict[str, Any]:
    caps = capabilities(pack)
    scheme = scheme_for_pack(pack, caps)
    version = pack.get("version") or (pack.get("metadata") or {}).get("version") or 1
    handlers_python: dict[str, str] = {}
    handlers_urisys: dict[str, str] = {}
    uri_patterns = [
        build_route(
            item,
            package_id=package_id,
            scheme=scheme,
            module_name=module_name,
            handlers_python=handlers_python,
            handlers_urisys=handlers_urisys,
        )
        for item in caps
    ]

    metadata = pack.get("metadata") or {}
    handlers: dict[str, Any] = {"python": handlers_python}
    if handlers_urisys:
        handlers["urisys"] = handlers_urisys
    manifest: dict[str, Any] = {
        "id": package_id,
        "version": version,
        "scheme": scheme,
        "description": pack.get("description")
        or metadata.get("description")
        or f"UriPack generated from Markpact {package_id}.",
        "generated_from": str(pack.get("generated_from") or "markpact"),
        "source_hash": source_hash,
        "uri_patterns": uri_patterns,
        "handlers": handlers,
    }
    for optional_key in ["policy", "runtime", "environment", "dependencies"]:
        if optional_key in pack:
            manifest[optional_key] = pack[optional_key]
    return manifest


__all__ = ["build_route", "compile_manifest"]
