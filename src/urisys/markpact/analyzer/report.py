"""Markpact analyze — definitions, flows, profile lint."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..flows import classify_flow, declared_uses, extract_flows, extract_protos
from ..profile import lint_markpact
from .resolver_lint import lint_process_resolver_stubs
from ..blocks import read_blocks
from ..pack import capabilities, load_pack_block, package_id, scheme_for_pack


def analyze_markpact(path: str | Path) -> dict[str, Any]:
    source_path = Path(path)
    blocks = read_blocks(source_path)
    pack = load_pack_block(source_path)
    caps = capabilities(pack)
    scheme = scheme_for_pack(pack, caps)
    uses = declared_uses(pack)
    flows = extract_flows(blocks)

    analyzed = []
    all_undeclared: set[str] = set()
    for flow in flows:
        info = classify_flow(flow["data"], pack_scheme=scheme, declared_uses=uses)
        all_undeclared.update(info["undeclared_uses"])
        analyzed.append({"id": flow["id"], **info})

    profile = lint_markpact(
        pack=pack,
        scheme=scheme,
        capabilities=caps,
        flows=flows,
        undeclared_schemes=sorted(all_undeclared),
    )

    resolver = lint_process_resolver_stubs(str(source_path.resolve())) if scheme == "process" and flows else None
    ok = not all_undeclared and profile["ok"] and (resolver is None or resolver.get("ok", True))

    return {
        "ok": ok,
        "package_id": package_id(pack, source_path),
        "scheme": scheme,
        "declared_uses": sorted(uses),
        "capabilities": len(caps),
        "protos": [name for name, _ in extract_protos(blocks)],
        "flows": analyzed,
        "use_cases": [f["id"] for f in analyzed if f["kind"] == "use_case"],
        "integrations": [f["id"] for f in analyzed if f["kind"] == "integration"],
        "undeclared_uses": sorted(all_undeclared),
        "profile": profile,
        "resolver": resolver,
        "errors": profile["errors"],
        "warnings": profile["warnings"],
    }
