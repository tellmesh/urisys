#!/usr/bin/env python3
"""Check Lenovo/example flow YAML URIs against pack manifest patterns.

Usage:
  python3 scripts/check_flow_uri_patterns.py
  python3 scripts/check_flow_uri_patterns.py --flows ../urisys-examples/lenovo-remote
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pack_registry import TELLMESH, pack_specs

_URI_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
_KNOWN_TARGETS = frozenset({"lenovo", "local", "linkedin"})


def _manifest_schemes(raw: dict) -> list[str]:
    if isinstance(raw.get("schemes"), list):
        return [str(s).strip() for s in raw["schemes"] if str(s).strip()]
    scheme = str(raw.get("scheme") or "").strip()
    return [scheme] if scheme else []


def manifest_path(spec) -> Path | None:
    if spec.layout == "flat":
        mf = spec.repo / "manifest.yaml"
    else:
        mf = spec.repo / spec.name / "manifest.yaml"
    return mf if mf.is_file() else None


def _patterns_from_manifest_file(mf: Path) -> list[str]:
    raw = yaml.safe_load(mf.read_text(encoding="utf-8")) or {}
    return [
        str(item.get("pattern", "")).strip()
        for item in (raw.get("uri_patterns") or [])
        if isinstance(item, dict) and item.get("pattern")
    ]


def _register_manifest_file(by_scheme: dict[str, list[str]], mf: Path) -> None:
    raw = yaml.safe_load(mf.read_text(encoding="utf-8")) or {}
    patterns = _patterns_from_manifest_file(mf)
    for scheme in _manifest_schemes(raw):
        by_scheme.setdefault(scheme, []).extend(patterns)


def load_patterns() -> dict[str, list[str]]:
    """scheme -> list of manifest patterns (with {placeholders})."""
    by_scheme: dict[str, list[str]] = {}
    for _name, spec in pack_specs().items():
        mod = spec.repo / spec.name if spec.layout != "flat" else spec.repo
        if not mod.is_dir():
            continue
        for mf in sorted(mod.glob("manifest*.yaml")):
            _register_manifest_file(by_scheme, mf)
    for extra in ("uriimg2nl",):
        extra_root = TELLMESH / extra
        for mf in sorted(extra_root.glob("**/manifest*.yaml")):
            _register_manifest_file(by_scheme, mf)
    node_mod = TELLMESH / "urisys-node" / "urisysnode"
    for mf in sorted(node_mod.glob("manifest*.yaml")):
        _register_manifest_file(by_scheme, mf)
    return by_scheme


def pattern_to_regex(pattern: str) -> re.Pattern[str]:
    parts: list[str] = []
    for chunk in re.split(r"(\{[^}]+\})", pattern):
        if chunk.startswith("{") and chunk.endswith("}"):
            parts.append("[^/]+")
        else:
            parts.append(re.escape(chunk))
    return re.compile("^" + "".join(parts) + "$")


def uri_candidates(uri: str) -> list[str]:
    """Direct URI plus variants without a leading target segment (kv://lenovo/runtime/...)."""
    if "://" not in uri:
        return [uri]
    scheme, rest = uri.split("://", 1)
    out = [uri]
    first = rest.split("/", 1)[0]
    if first in _KNOWN_TARGETS and "/" in rest:
        out.append(f"{scheme}://{rest.split('/', 1)[1]}")
    return out


def uri_matches(uri: str, patterns: list[str]) -> bool:
    for candidate in uri_candidates(uri):
        for pat in patterns:
            if pattern_to_regex(pat).match(candidate):
                return True
    return False


def collect_flow_uris(flow_dir: Path) -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for path in sorted(flow_dir.glob("**/*.uri.flow.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        steps = data.get("do") or data.get("steps") or []
        if not isinstance(steps, list):
            continue
        for step in steps:
            if not isinstance(step, dict):
                continue
            uri = str(step.get("uri") or "").strip()
            if _URI_RE.match(uri):
                out.append((path, uri))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate flow URIs against manifest patterns.")
    parser.add_argument(
        "--flows",
        action="append",
        default=[str(TELLMESH / "urisys-examples" / "lenovo-remote")],
        help="Directory with *.uri.flow.yaml files (repeatable).",
    )
    args = parser.parse_args()

    patterns = load_patterns()
    unknown: list[str] = []
    checked = 0

    for flow_root in args.flows:
        root = Path(flow_root)
        if not root.is_dir():
            print(f"SKIP missing flow dir: {root}")
            continue
        for path, uri in collect_flow_uris(root):
            checked += 1
            scheme = urlsplit(uri).scheme
            pats = patterns.get(scheme, [])
            rel = path.relative_to(TELLMESH) if path.is_relative_to(TELLMESH) else path
            if uri_matches(uri, pats):
                print(f"OK   {rel}: {uri}")
            else:
                print(f"MISS {rel}: {uri} (scheme={scheme}, patterns={len(pats)})")
                unknown.append(f"{rel}: {uri}")

    print(f"\nDone: checked={checked} miss={len(unknown)}")
    return 1 if unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())
