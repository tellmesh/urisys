"""Markpact profile v1alpha — static lint helpers for ``urisys markpact analyze``."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import urlsplit

from .flows import flow_uris

IssueSeverity = Literal["error", "warning"]


@dataclass(frozen=True)
class LintIssue:
    code: str
    severity: IssueSeverity
    message: str
    location: str | None = None


def _issue(code: str, severity: IssueSeverity, message: str, location: str | None = None) -> LintIssue:
    return LintIssue(code=code, severity=severity, message=message, location=location)


def _issue_message(issue: LintIssue) -> str:
    return f"{issue.code}: {issue.message}"


_FLOW_FEATURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "linear": re.compile(r"."),
    "step_id": re.compile(r"\bid\s*:"),
    "after": re.compile(r"\bafter\s*:"),
    "save_as": re.compile(r"\bsave_as\s*:"),
    "ref": re.compile(r"\$\{[^}]+\}"),
    "if": re.compile(r"\bif\s*:"),
    "expect": re.compile(r"^expect\s*:", re.M),
    "inputs": re.compile(r"^inputs\s*:", re.M),
}


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


def _step_features(steps: list[Any], features: set[str]) -> None:
    for step in steps:
        if not isinstance(step, dict):
            continue
        if step.get("id"):
            features.add("step_id")
        if step.get("after"):
            features.add("after")
        if step.get("save_as"):
            features.add("save_as")
        if step.get("if"):
            features.add("if")


def _flow_level_features(flow_data: dict[str, Any], features: set[str]) -> None:
    if flow_data.get("expect"):
        features.add("expect")
    if flow_data.get("inputs"):
        features.add("inputs")


def _text_pattern_features(text: str, features: set[str]) -> None:
    for pattern_name, pattern in _FLOW_FEATURE_PATTERNS.items():
        if pattern_name not in features and pattern.search(text):
            features.add(pattern_name)


def _flow_features(flow_data: dict[str, Any], raw_yaml: str = "") -> set[str]:
    features: set[str] = set()
    text = raw_yaml or ""
    steps = flow_data.get("do") or []
    if steps:
        features.add("linear")
    _step_features(steps, features)
    _flow_level_features(flow_data, features)
    _text_pattern_features(text, features)
    uris = " ".join(flow_uris(flow_data))
    if "${" in uris or "${" in text:
        features.add("ref")
    return features


def _required_features(flow_data: dict[str, Any]) -> set[str]:
    declared = flow_data.get("requires_features")
    if isinstance(declared, list):
        return {str(x).strip() for x in declared if str(x).strip()}
    return set()


def _validate_scheme_requirements(
    pack: dict[str, Any], scheme: str
) -> tuple[list[str], list[str], set[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    schemes_required = declared_schemes(pack)
    packs_default = declared_packs(pack)
    return errors, warnings, schemes_required, packs_default


def _build_flow_profiles(
    flows: list[dict[str, Any]], scheme: str, warnings: list[str], issues: list[LintIssue]
) -> list[dict[str, Any]]:
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

        flow_profiles.append(
            {
                "id": flow_id,
                "profile": (data.get("flow") or {}).get("profile"),
                "features": sorted(features),
                "requires_features": sorted(required),
            }
        )
    return flow_profiles


def _cross_check_schemes(
    flows: list[dict[str, Any]], schemes_required: set[str], scheme: str, warnings: list[str]
) -> list[str]:
    if not schemes_required:
        return warnings
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
    return warnings


def lint_markpact(
    *,
    pack: dict[str, Any],
    scheme: str,
    capabilities: list[dict[str, Any]],
    flows: list[dict[str, Any]],
    undeclared_schemes: list[str],
) -> dict[str, Any]:
    from .analyzer.lint import run_lint

    return run_lint(
        pack=pack,
        scheme=scheme,
        capabilities=capabilities,
        flows=flows,
        undeclared_schemes=undeclared_schemes,
    )
