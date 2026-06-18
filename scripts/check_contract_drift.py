#!/usr/bin/env python3
"""Check manifest.yaml vs hand-written UriContract Markpacts (core surface drift).

Scans tellmesh capability repos for ``markpacts/*.contract.markpact.md`` and
compares each to the pack ``manifest.yaml`` via ``contract_gen.diff_manifest_contract``.

Usage:
  python3 scripts/check_contract_drift.py
  python3 scripts/check_contract_drift.py --pack urikvm
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _SCRIPTS.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pack_registry import TELLMESH, pack_specs
from urisys.managers import contract_gen

EXTRA = ("uriimg2nl",)


def manifest_path(spec) -> Path | None:
    if spec.layout == "flat":
        mf = spec.repo / "manifest.yaml"
    else:
        mf = spec.repo / spec.name / "manifest.yaml"
    return mf if mf.is_file() else None


def contract_paths(spec) -> list[Path]:
    markpacts = spec.repo / "markpacts"
    if not markpacts.is_dir():
        return []
    return sorted(markpacts.glob("*.contract.markpact.md"))


_TRANSPORT_CONTRACT_IDS = frozenset({"urisys-node.service"})


def check_pair(manifest: Path, contract: Path) -> list[str]:
    c = contract_gen.load_contract_block(contract)
    if str((c.get("metadata") or {}).get("id", "")) in _TRANSPORT_CONTRACT_IDS:
        return []
    m = contract_gen.load_manifest(manifest)
    return contract_gen.diff_manifest_contract(m, c)


def _check_spec(name: str, spec) -> tuple[int, int, int]:
    mf = manifest_path(spec)
    contracts = contract_paths(spec)
    if not mf or not contracts:
        return 0, 0, 1

    ok = 0
    drift = 0
    for contract in contracts:
        label = contract.relative_to(TELLMESH) if contract.is_relative_to(TELLMESH) else contract
        issues = check_pair(mf, contract)
        if issues:
            print(f"DRIFT {label}")
            for item in issues:
                print(f"  - {item}")
            drift += 1
        else:
            print(f"OK   {label}")
            ok += 1
    return ok, drift, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check manifest vs UriContract Markpact drift.")
    parser.add_argument("--pack", action="append", default=[], help="Only these pack names.")
    args = parser.parse_args()
    selected = set(args.pack) if args.pack else None

    specs = dict(pack_specs())
    for name in EXTRA:
        repo = TELLMESH / name
        if repo.is_dir() and name not in specs:
            from pack_registry import _pack

            specs[name] = _pack(name, repo_readme=f"{name}:// URI capability pack.")

    ok = 0
    drift = 0
    skip = 0

    for name, spec in sorted(specs.items()):
        if selected and name not in selected:
            continue
        s_ok, s_drift, s_skip = _check_spec(name, spec)
        ok += s_ok
        drift += s_drift
        skip += s_skip

    print(f"\nDone: ok={ok} drift={drift} skip={skip}")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
