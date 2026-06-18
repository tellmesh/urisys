"""Extraction + classification of showcase Markpact blocks (proto, flow, module)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from .models import MarkpactBlock, MarkpactError, safe_identifier

try:  # local import to avoid cycle at module import time
    import yaml
except Exception:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def extract_protos(blocks: list[MarkpactBlock]) -> list[tuple[str, str]]:
    """Return ``(filename, content)`` for every ``markpact:proto`` block."""
    out: list[tuple[str, str]] = []
    for i, block in enumerate(b for b in blocks if b.kind == "proto"):
        name = block.meta.get("path") or block.meta.get("name") or f"types_{i}.proto"
        if not name.endswith(".proto"):
            name = f"{safe_identifier(name)}.proto"
        out.append((name, block.content))
    return out


def extract_modules(blocks: list[MarkpactBlock]) -> list[tuple[str, str]]:
    """Return ``(relative_path, source)`` for every ``markpact:module`` block."""
    out: list[tuple[str, str]] = []
    for i, block in enumerate(b for b in blocks if b.kind == "module"):
        path = block.meta.get("path") or block.meta.get("name") or f"module_{i}.py"
        path = path.replace("\\", "/").lstrip("/")
        if ".." in path.split("/"):
            raise MarkpactError(f"markpact:module path may not contain '..': {path!r}")
        out.append((path, block.content))
    return out


def extract_flows(blocks: list[MarkpactBlock]) -> list[dict[str, Any]]:
    """Return parsed embedded flows. Each item: ``{id, data, raw}``."""
    flows: list[dict[str, Any]] = []
    for block in (b for b in blocks if b.kind == "flow" and b.lang in {"yaml", "yml"}):
        if yaml is None:  # pragma: no cover
            raise MarkpactError("PyYAML is required to parse markpact:flow blocks.")
        data = yaml.safe_load(block.content) or {}
        if not isinstance(data, dict):
            raise MarkpactError("markpact:flow block must contain a YAML mapping.")
        flow_id = block.meta.get("id") or (data.get("flow") or {}).get("id") or f"flow_{len(flows)}"
        flows.append({"id": flow_id, "data": data, "raw": block.content})
    return flows


def flow_uris(flow_data: dict[str, Any]) -> list[str]:
    """Extract the URIs referenced by a flow's ``do`` steps (all step shapes)."""
    uris: list[str] = []
    for step in flow_data.get("do") or []:
        if isinstance(step, str):
            uris.append(step)
        elif isinstance(step, dict):
            if "uri" in step:
                uris.append(str(step["uri"]))
            else:  # compact {uri: payload} form
                key = next(iter(step), None)
                if isinstance(key, str) and "://" in key:
                    uris.append(key)
    return uris


def _scheme(uri: str) -> str:
    return urlsplit(uri).scheme


DOMAIN_SCHEME_PROVIDERS: dict[str, str] = {
    "package": "shell",
}


def _provider_scheme(scheme: str) -> str:
    return DOMAIN_SCHEME_PROVIDERS.get(scheme, scheme)


def classify_flow(flow_data: dict[str, Any], *, pack_scheme: str, declared_uses: set[str]) -> dict[str, Any]:
    """Classify a flow as ``use_case`` or ``integration`` and report missing deps."""
    uris = flow_uris(flow_data)
    schemes = [s for s in (_scheme(u) for u in uris) if s]
    foreign = sorted({s for s in schemes if s and s != pack_scheme})
    kind = "use_case" if not foreign else "integration"
    undeclared = sorted(
        s
        for s in foreign
        if s not in declared_uses and _provider_scheme(s) not in declared_uses
    )
    return {
        "kind": kind,
        "schemes": sorted(set(schemes)),
        "foreign_schemes": foreign,
        "undeclared_uses": undeclared,
        "steps": len(uris),
        "requires": {"schemes": sorted(set(schemes))},
    }


def declared_uses(pack: dict[str, Any]) -> set[str]:
    """Schemes a pack declares it integrates with (``requires.schemes`` or legacy ``uses``)."""
    from .profile import declared_schemes

    return declared_schemes(pack)
