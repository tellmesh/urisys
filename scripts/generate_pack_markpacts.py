#!/usr/bin/env python3
"""Generate thin ``*.markpact.md`` for tellmesh uri* capability packs.

Canonical output: ``{pack}/markpacts/{name}.markpact.md`` (handlers stay in repo as python://).

Usage:
  python3 scripts/generate_pack_markpacts.py
  python3 scripts/generate_pack_markpacts.py --pack urikvm --check
  python3 scripts/generate_pack_markpacts.py --aggregate   # copy/summary to markpact-contracts/packs/
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pack_registry import TELLMESH, PackSpec, pack_specs

AGGREGATE_DIR = TELLMESH / "markpact-contracts" / "packs"
SKIP_PACKS = frozenset(
    {
        "uricontrol",
        "urioperators",
        "urikvmedge",
        "urirdpedge",
        "uristepperedge",
        "uribrowseredge",
        "labedge",
    }
)
EXTRA_PACK_DIRS = ("uriimg2nl",)


def repo_module_dir(spec: PackSpec) -> Path:
    if spec.layout == "flat":
        return spec.repo
    return spec.repo / spec.name


def _extra_specs() -> dict[str, PackSpec]:
    from pack_registry import _pack

    out: dict[str, PackSpec] = {}
    for name in EXTRA_PACK_DIRS:
        repo = TELLMESH / name
        if repo.is_dir():
            out[name] = _pack(name, repo_readme=f"{name}:// URI capability pack.")
    return out


def _scheme(uri: str) -> str:
    return urlsplit(uri).scheme if "://" in uri else ""


def _fill_pattern(pattern: str) -> str:
    return re.sub(
        r"\{[^}]+\}",
        lambda m: {
            "host": "local",
            "session": "default",
            "device": "mock",
            "axis": "x",
            "command": "echo",
            "namespace": "demo",
            "key": "k",
            "prefix": "p",
            "stream": "events",
            "path": "/tmp/log",
            "target": "local",
            "monitor": "primary",
            "name": "demo",
            "resource": "demo",
        }.get(m.group(0)[1:-1], "demo"),
        pattern,
    )


def _capabilities(manifest: dict[str, Any], handlers: dict[str, str]) -> list[dict[str, Any]]:
    caps: list[dict[str, Any]] = []
    for item in manifest.get("uri_patterns") or []:
        op = str(item["operation"])
        cap: dict[str, Any] = {
            "id": op.replace(".", "-"),
            "uri": item["pattern"],
            "kind": item.get("kind", "query"),
            "operation": op,
            "handler": handlers.get(op) or f"python://{manifest.get('id', 'pack')}.handlers:handler",
            "side_effects": bool(item.get("side_effects", item.get("kind") == "command")),
            "approval": item.get("approval", "required" if item.get("kind") == "command" else "not_required"),
        }
        for key in ("command_type", "query_type", "result_type", "success_event_type", "description"):
            if key in item:
                cap[key] = item[key]
        caps.append(cap)
    return caps


def _tests(caps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tests: list[dict[str, Any]] = []
    ctx = {"approved": True, "dry_run": True, "environment": "mock"}
    for kind in ("query", "command"):
        for cap in caps:
            if cap.get("kind") != kind:
                continue
            entry: dict[str, Any] = {
                "id": f"{cap['operation']}_{kind}",
                "uri": _fill_pattern(cap["uri"]),
                "context": dict(ctx),
                "expect": {"ok": True, "operation": cap["operation"]},
            }
            if kind == "command":
                entry["payload"] = {}
            tests.append(entry)
            break
    return tests


def _use_case_flow(manifest: dict[str, Any], caps: list[dict[str, Any]]) -> dict[str, Any]:
    scheme = manifest.get("scheme") or (_scheme(caps[0]["uri"]) if caps else "demo")
    steps: list[Any] = []
    for cap in caps[:3]:
        uri = _fill_pattern(cap["uri"])
        steps.append({uri: {}} if cap.get("kind") == "command" else uri)
    flow_id = f"{scheme}-smoke"
    return {
        "flow": {
            "id": flow_id,
            "description": f"Smoke {scheme}:// routes (generated from manifest).",
        },
        "defaults": {"approved": True, "dry_run": True},
        "do": steps or [f"{scheme}://local/query/status"],
    }


def _run_block(scheme: str, flow_id: str, uses: list[str], port: int) -> dict[str, Any]:
    return {
        "scheme": scheme,
        "default": "flow",
        "modes": ["pack", "service", "flow", "interface", "adapter"],
        "service": {"port_hint": port, "path": "/uri/call"},
        "flow": {"ids": [flow_id]},
        "uses": uses,
        "adapter": {"call": "POST /uri/call", "events": "GET /events"},
    }


def _default_port(scheme: str) -> int:
    return {
        "kvm": 8794,
        "rdp": 8795,
        "stepper": 8791,
        "browser": 8792,
        "env": 8793,
        "stt": 8796,
    }.get(scheme, 8789)


def _render(
    *,
    file_stem: str,
    manifest: dict[str, Any],
    repo_dir: Path,
    manifest_file: Path,
) -> str:
    handlers = (manifest.get("handlers") or {}).get("python") or {}
    caps = _capabilities(manifest, handlers)
    scheme = manifest.get("scheme") or (_scheme(caps[0]["uri"]) if caps else file_stem)
    pack_id = str(manifest.get("id", file_stem))
    version = str(manifest.get("version", "0.1.0"))
    foreign = sorted({s for c in caps for s in [_scheme(c["uri"])] if s and s != scheme})
    uses = [f"{u}://" for u in foreign]

    pack_yaml: dict[str, Any] = {
        "apiVersion": "urisys.io/v1",
        "kind": "UriPack",
        "metadata": {"id": pack_id, "version": version, "language": "python"},
        "description": manifest.get("description") or f"{scheme}:// capability pack.",
        "schemes": [scheme],
        "capabilities": caps,
        "policy": {"default": "deny_mutations_without_approval"},
        "runtime": {
            "default_environment": "real",
            "supports": ["mock", "local", "docker"],
            "expose": ["pack", "service", "flow", "interface", "adapter"],
        },
    }
    if uses:
        pack_yaml["uses"] = uses

    tests = _tests(caps)
    flow = _use_case_flow(manifest, caps)
    flow_id = flow["flow"]["id"]
    run_cfg = _run_block(scheme, flow_id, uses, _default_port(scheme))

    rel_repo = repo_dir.relative_to(TELLMESH) if repo_dir.is_relative_to(TELLMESH) else repo_dir
    rel_manifest = manifest_file.relative_to(TELLMESH) if manifest_file.is_relative_to(TELLMESH) else manifest_file
    rel_markpact = f"{rel_repo}/markpacts/{file_stem}.markpact.md"

    return "\n".join(
        [
            f"# UriPack: {pack_id}",
            "",
            f"Thin Markpact — capabilities from [`{rel_manifest}`]({rel_manifest}).",
            f"Handlers: existing ``python://`` refs (code in `{rel_repo}/`, not duplicated here).",
            "",
            "Generated by `urisys/scripts/generate_pack_markpacts.py`.",
            "",
            "```yaml markpact:pack",
            yaml.safe_dump(pack_yaml, sort_keys=False, allow_unicode=True).strip(),
            "```",
            "",
            "```yaml markpact:run",
            yaml.safe_dump(run_cfg, sort_keys=False, allow_unicode=True).strip(),
            "```",
            "",
            "```yaml markpact:tests",
            yaml.safe_dump({"tests": tests}, sort_keys=False, allow_unicode=True).strip(),
            "```",
            "",
            f"```yaml markpact:flow id={flow_id}",
            yaml.safe_dump(flow, sort_keys=False, allow_unicode=True).strip(),
            "```",
            "",
            "```markdown markpact:docs",
            "## Unpack → `.markpact/`",
            "",
            "```bash",
            f"cd {rel_repo}",
            f"export TELLMESH_ROOT={TELLMESH}",
            f"PACK=markpacts/{file_stem}.markpact.md",
            "urisys markpact run \"$PACK\" --as flow --approve --dry-run",
            "urisys markpact run \"$PACK\" --as pack",
            "urisys markpact run \"$PACK\" --as service --port "
            + str(_default_port(scheme)),
            "urisys markpact run \"$PACK\" --as interface",
            "urisys markpact run \"$PACK\" --as adapter",
            "```",
            "",
            f"- Source manifest: `{rel_manifest}`",
            f"- Requires: `pip install -e {rel_repo}` or `TELLMESH_ROOT` for python:// handlers",
            "```",
            "",
        ]
    )


def _split_by_scheme(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    patterns = manifest.get("uri_patterns") or []
    by_scheme: dict[str, list[dict[str, Any]]] = {}
    for item in patterns:
        scheme = _scheme(str(item.get("pattern", "")))
        if scheme:
            by_scheme.setdefault(scheme, []).append(item)
    if len(by_scheme) <= 1:
        return [manifest]
    handlers = (manifest.get("handlers") or {}).get("python") or {}
    base_id = str(manifest.get("id") or "pack")
    out: list[dict[str, Any]] = []
    for scheme, pats in sorted(by_scheme.items()):
        ops = {str(p["operation"]) for p in pats}
        split = dict(manifest)
        split["scheme"] = scheme
        split["id"] = f"{base_id}-{scheme}" if len(by_scheme) > 1 else base_id
        split["uri_patterns"] = pats
        split["handlers"] = {"python": {k: v for k, v in handlers.items() if k in ops}}
        out.append(split)
    return out


def manifest_files(spec: PackSpec) -> list[Path]:
    mod = repo_module_dir(spec)
    return sorted(p for p in mod.glob("manifest*.yaml") if p.is_file())


def _file_stem(spec: PackSpec, manifest: dict[str, Any], manifest_path: Path) -> str:
    if manifest_path.name != "manifest.yaml":
        return f"{spec.name}-{manifest_path.stem.replace('manifest.', '')}"
    mid = str(manifest.get("id", spec.name))
    if mid != spec.name and "-" in mid:
        return mid.replace("_", "-")
    return spec.name


def generate_for_spec(spec: PackSpec) -> list[tuple[Path, str]]:
    outputs: list[tuple[Path, str]] = []
    out_dir = spec.repo / "markpacts"
    for mf in manifest_files(spec):
        raw = yaml.safe_load(mf.read_text(encoding="utf-8")) or {}
        for manifest in _split_by_scheme(raw):
            stem = _file_stem(spec, manifest, mf)
            content = _render(
                file_stem=stem,
                manifest=manifest,
                repo_dir=spec.repo,
                manifest_file=mf,
            )
            outputs.append((out_dir / f"{stem}.markpact.md", content))
    return outputs


def _process_spec(
    spec: PackSpec,
    *,
    check: bool,
    aggregate: bool,
    changed: int,
    written: int,
) -> tuple[int, int]:
    for out_path, content in generate_for_spec(spec):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        label = out_path.relative_to(TELLMESH) if out_path.is_relative_to(TELLMESH) else out_path
        if out_path.is_file() and out_path.read_text(encoding="utf-8") == content:
            print(f"OK  {label}")
        elif check:
            print(f"DRIFT {label}")
            changed += 1
        else:
            out_path.write_text(content, encoding="utf-8")
            written += 1
            print(f"WROTE {label}")
        if aggregate and not check:
            AGGREGATE_DIR.mkdir(parents=True, exist_ok=True)
            agg = AGGREGATE_DIR / out_path.name
            shutil.copy2(out_path, agg)
    return changed, written


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate thin pack Markpacts from manifest.yaml.")
    parser.add_argument("--pack", action="append", default=[], help="Only these pack names.")
    parser.add_argument("--check", action="store_true", help="Exit 1 if generated files would change.")
    parser.add_argument("--aggregate", action="store_true", help="Also copy to markpact-contracts/packs/.")
    args = parser.parse_args()

    specs = {**pack_specs(), **_extra_specs()}
    selected = set(args.pack) if args.pack else None
    changed = 0
    written = 0

    for name, spec in sorted(specs.items()):
        if name in SKIP_PACKS:
            continue
        if selected and name not in selected:
            continue
        if not repo_module_dir(spec).is_dir():
            print(f"SKIP {name}: no module dir")
            continue
        changed, written = _process_spec(
            spec, check=args.check, aggregate=args.aggregate, changed=changed, written=written
        )

    if args.check and changed:
        return 1
    print(f"\nDone: written={written} drift={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
