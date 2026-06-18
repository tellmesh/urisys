"""Markpact profile v1alpha — static lint rules for ``urisys markpact analyze``."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

from .markpact_flows import flow_uris

_FLOW_FEATURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "linear": re.compile(r"."),  # any flow
    "step_id": re.compile(r"\bid\s*:"),
    "after": re.compile(r"\bafter\s*:"),
    "save_as": re.compile(r"\bsave_as\s*:"),
    "ref": re.compile(r"\$\{[^}]+\}"),
    "if": re.compile(r"\bif\s*:"),
    "expect": re.compile(r"^expect\s*:", re.M),
    "inputs": re.compile(r"^inputs\s*:", re.M),
}

_URI_FLOW_LEVELS: list[tuple[str, set[str]]] = [
    ("uri-flow/level-0", {"linear"}),
    ("uri-flow/level-1", {"linear", "step_id", "after"}),
    ("uri-flow/level-2", {"linear", "step_id", "after", "save_as", "ref", "if", "inputs"}),
    ("uri-flow/v1", {"linear", "step_id", "after", "save_as", "ref", "if", "expect", "inputs"}),
]


def declared_schemes(pack: dict[str, Any]) -> set[str]:
    """Semantic schemes required by a pack (``requires.schemes`` or legacy flat ``uses``)."""
    requires = pack.get("requires")
    if isinstance(requires, dict):
        schemes = requires.get("schemes")
        if isinstance(schemes, list):
            return {str(s).strip() for s in schemes if str(s).strip()}
    raw: list[Any] = []
    for key in ("uses", "dependencies"):
        value = pack.get(key)
        if isinstance(value, list):
            raw.extend(value)
    out: set[str] = set()
    for item in raw:
        text = str(item).strip()
        if not text or text.startswith("uri"):
            continue
        out.add(text.split("://", 1)[0] if "://" in text else text)
    return out


def declared_packs(pack: dict[str, Any]) -> list[str]:
    """Default implementation packs (``uses.packs``)."""
    uses = pack.get("uses")
    if isinstance(uses, dict):
        packs = uses.get("packs")
        if isinstance(packs, list):
            return [str(p).strip() for p in packs if str(p).strip()]
    return []


def _cap_uri(cap: dict[str, Any]) -> str:
    return str(cap.get("uri") or cap.get("pattern") or "")


def _flow_features(flow_data: dict[str, Any], raw_yaml: str = "") -> set[str]:
    features: set[str] = set()
    text = raw_yaml or ""
    steps = flow_data.get("do") or []
    if steps:
        features.add("linear")
    for step in steps:
        if isinstance(step, dict):
            if step.get("id"):
                features.add("step_id")
            if step.get("after"):
                features.add("after")
            if step.get("save_as"):
                features.add("save_as")
            if step.get("if"):
                features.add("if")
    if flow_data.get("expect"):
        features.add("expect")
    if flow_data.get("inputs"):
        features.add("inputs")
    for pattern_name, pattern in _FLOW_FEATURE_PATTERNS.items():
        if pattern_name in features:
            continue
        if text and pattern.search(text):
            features.add(pattern_name)
    uris = " ".join(flow_uris(flow_data))
    if "${" in uris or "${" in text:
        features.add("ref")
    return features


def _required_features(flow_data: dict[str, Any]) -> set[str]:
    """Only explicit ``requires_features`` is enforced; ``flow.profile`` is documentary."""
    declared = flow_data.get("requires_features")
    if isinstance(declared, list):
        return {str(x).strip() for x in declared if str(x).strip()}
    return set()


def lint_markpact(
    *,
    pack: dict[str, Any],
    scheme: str,
    capabilities: list[dict[str, Any]],
    flows: list[dict[str, Any]],
    undeclared_schemes: list[str],
) -> dict[str, Any]:
    """Return ``{ok, errors, warnings, requires, uses_packs, flow_profiles}``."""
    errors: list[str] = []
    warnings: list[str] = []

    schemes_required = declared_schemes(pack)
    packs_default = declared_packs(pack)

    if scheme == "process" and not schemes_required and not pack.get("requires"):
        warnings.append("process pack should declare requires.schemes explicitly (v1alpha)")

    if undeclared_schemes:
        for s in undeclared_schemes:
            errors.append(f"flow uses undeclared scheme {s!r} (add to requires.schemes)")

    requires_caps = (pack.get("requires") or {}).get("capabilities") if isinstance(pack.get("requires"), dict) else None
    if isinstance(requires_caps, list) and requires_caps:
        for cap_name in requires_caps:
            if "." not in str(cap_name):
                warnings.append(f"requires.capabilities entry {cap_name!r} should be namespaced")

    for cap in capabilities:
        op = str(cap.get("operation") or "").strip()
        if op and "." not in op:
            warnings.append(f"operation {op!r} should be namespaced (e.g. stepper.status)")

        uri = _cap_uri(cap)
        kind = str(cap.get("kind") or "").strip()
        if uri and kind:
            if "/query/" in uri and kind != "query":
                errors.append(f"URI {uri!r} contains /query/ but kind is {kind!r}")
            if "/command/" in uri and kind != "command":
                errors.append(f"URI {uri!r} contains /command/ but kind is {kind!r}")

        if kind == "command" and cap.get("side_effects") and str(cap.get("approval") or "") == "not_required":
            errors.append(f"command {op or uri!r} has side_effects:true but approval:not_required")

        if scheme == "process":
            handler = str(cap.get("handler") or "")
            if handler and not handler.startswith("urisys://flow/"):
                errors.append(f"process capability {op!r} handler must be urisys://flow/<id>, got {handler!r}")

    flow_profiles: list[dict[str, Any]] = []
    for flow in flows:
        flow_id = flow["id"]
        data = flow["data"]
        raw = flow.get("raw") or ""
        features = _flow_features(data, raw)
        required = _required_features(data)
        missing_features = sorted(required - features) if required else []
        if missing_features:
            warnings.append(f"flow {flow_id!r} declares features {sorted(required)} but missing: {missing_features}")

        if scheme == "process" and not data.get("expect"):
            warnings.append(f"flow {flow_id!r} has no expect: block (v1alpha production processes)")

        for uri in flow_uris(data):
            if "/image/latest/" in uri:
                warnings.append(f"flow {flow_id!r} uses implicit latest state in {uri!r}")

        flow_profiles.append(
            {
                "id": flow_id,
                "profile": (data.get("flow") or {}).get("profile"),
                "features": sorted(features),
                "requires_features": sorted(required),
            }
        )

    # Cross-check requires.schemes vs flow usage
    if schemes_required:
        used: set[str] = set()
        for flow in flows:
            for uri in flow_uris(flow["data"]):
                sch = urlsplit(uri).scheme
                if sch and sch != scheme:
                    used.add(sch)
        extra = sorted(used - schemes_required - {"package"})
        missing = sorted(schemes_required - used)
        if extra:
            warnings.append(f"requires.schemes omits flow schemes: {extra}")
        if missing and scheme == "process":
            warnings.append(f"requires.schemes lists unused schemes: {missing}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "requires": {"schemes": sorted(schemes_required), "capabilities": requires_caps or []},
        "uses_packs": packs_default,
        "flow_profiles": flow_profiles,
        "profile": "markpact-v1alpha",
    }
