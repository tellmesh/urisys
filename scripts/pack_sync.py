#!/usr/bin/env python3
"""Sync capability packs: urisys monorepo ↔ tellmesh/* sibling repos.

Canonical source after migration: tellmesh/{repo}/ (no vendored duplicate in urisys).

Usage:
  python3 scripts/pack_sync.py to-repo --all      # push remaining vendored → sibling (once)
  python3 scripts/pack_sync.py promote --all      # to-repo + remove vendored copies
  python3 scripts/pack_sync.py check --all        # drift or missing sibling
  python3 scripts/pack_sync.py init-repo urikvmedge
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pack_registry import (
    ROOT,
    SIBLING_ONLY,
    TELLMESH,
    PackSpec,
    pack_specs,
    sibling_uv_path,
)


def repo_module_dir(spec: PackSpec) -> Path:
    if spec.module_dir:
        return spec.repo / spec.module_dir
    if spec.layout == "flat":
        return spec.repo
    return spec.repo / spec.name


def vendored_module_dir(spec: PackSpec) -> Path:
    if spec.vendored is None:
        raise FileNotFoundError(f"no vendored path for {spec.name}")
    return spec.vendored


def read_version(path: Path) -> str:
    pyproject = path / "pyproject.toml"
    if pyproject.is_file():
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        return str(data["project"]["version"]).strip()
    version_file = path / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    return "0.1.0"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_file(src: Path, dst: Path, *, dry_run: bool) -> bool:
    if not src.is_file():
        return False
    if dst.is_file() and file_hash(src) == file_hash(dst):
        return False
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return True


def sync_to_repo(spec: PackSpec, *, dry_run: bool = False, tests: bool = True) -> list[str]:
    changed: list[str] = []
    if spec.vendored is None or not spec.vendored.is_dir():
        return changed
    src_dir = vendored_module_dir(spec)
    dst_dir = repo_module_dir(spec)
    if not src_dir.is_dir():
        raise FileNotFoundError(f"vendored pack missing: {src_dir}")

    for name in spec.module_files:
        src = src_dir / name
        if sync_file(src, dst_dir / name, dry_run=dry_run):
            changed.append(f"{spec.name}/{name}")

    version = read_version(spec.vendored)
    version_path = spec.repo / "VERSION"
    if not version_path.is_file() or version_path.read_text(encoding="utf-8").strip() != version:
        if not dry_run:
            version_path.parent.mkdir(parents=True, exist_ok=True)
            version_path.write_text(f"{version}\n", encoding="utf-8")
        changed.append(f"{spec.name}/VERSION")

    if tests and spec.test_files:
        tests_dst = spec.repo / "tests"
        tests_src = TELLMESH / "urikvm-docker" / "tests"
        for test_name in spec.test_files:
            src = tests_src / test_name
            if sync_file(src, tests_dst / test_name, dry_run=dry_run):
                changed.append(f"{spec.name}/tests/{test_name}")

    return changed


def check_drift(spec: PackSpec) -> list[str]:
    if not spec.repo.is_dir():
        return [f"{spec.name}: repo missing at {spec.repo}"]
    if spec.vendored is None or not spec.vendored.exists():
        return _check_promoted(spec)
    drifts: list[str] = []
    src_dir = vendored_module_dir(spec)
    dst_dir = repo_module_dir(spec)
    for name in spec.module_files:
        src = src_dir / name
        dst = dst_dir / name
        if not src.is_file() and name == "manifest.yaml":
            continue
        if not src.is_file():
            drifts.append(f"{spec.name}: vendored missing {name}")
            continue
        if not dst.is_file():
            drifts.append(f"{spec.name}: repo missing {name}")
            continue
        if file_hash(src) != file_hash(dst):
            drifts.append(f"{spec.name}: drift {name}")
    try:
        vend_ver = read_version(spec.vendored)
    except FileNotFoundError:
        drifts.append(f"{spec.name}: vendored pyproject.toml missing")
        return drifts
    version_path = spec.repo / "VERSION"
    repo_ver = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    if repo_ver != vend_ver:
        drifts.append(f"{spec.name}: version vendored={vend_ver} repo={repo_ver or '?'}")
    return drifts


def _check_promoted(spec: PackSpec) -> list[str]:
    issues: list[str] = []
    dst_dir = repo_module_dir(spec)
    if not dst_dir.is_dir():
        issues.append(f"{spec.name}: promoted but repo module dir missing {dst_dir}")
        return issues
    if spec.vendored is not None and spec.vendored.is_dir():
        issues.append(f"{spec.name}: vendored copy still present at {spec.vendored} (run promote)")
    if not (spec.repo / "pyproject.toml").is_file():
        issues.append(f"{spec.name}: repo missing pyproject.toml")
    return issues


def remove_vendored(spec: PackSpec, *, dry_run: bool = False) -> bool:
    if spec.vendored is None or not spec.vendored.is_dir():
        return False
    if dry_run:
        print(f"would remove {spec.vendored}")
        return True
    shutil.rmtree(spec.vendored)
    return True


def _repo_pyproject(spec: PackSpec) -> str:
    version_path = spec.vendored / "pyproject.toml" if spec.vendored and (spec.vendored / "pyproject.toml").is_file() else spec.repo / "pyproject.toml"
    version = read_version(version_path.parent) if version_path.is_file() else "0.1.0"
    extras_lines = []
    for extra_name, deps in spec.optional_extras.items():
        dep_str = ", ".join(f'"{d}"' for d in deps)
        extras_lines.append(f'{extra_name} = [{dep_str}]')
    optional_block = ""
    if extras_lines:
        optional_block = "\n[project.optional-dependencies]\n" + "\n".join(extras_lines) + '\ndev = ["pytest>=8.0", "goal>=2.1.0"]\n'
    package_data = ""
    if (repo_module_dir(spec) / "manifest.yaml").is_file() or (spec.vendored and (spec.vendored / "manifest.yaml").is_file()):
        package_data = f'\n[tool.setuptools.package-data]\n{spec.name} = ["manifest.yaml"]\n'
    deps = ['"uricore>=0.1.0"'] + [f'"{d}"' for d in spec.extra_deps]
    deps_str = ", ".join(deps)
    if spec.layout == "flat":
        setuptools = f"""
[tool.setuptools]
packages = ["{spec.name}"]
package-dir = {{ "{spec.name}" = "." }}
"""
    else:
        setuptools = f"""
[tool.setuptools.packages.find]
where = ["."]
include = ["{spec.name}*"]
"""
    uv_extra = ""
    if any("urioperators" in d for d in spec.extra_deps):
        uv_extra = '\nurioperators = { path = "../urioperators", editable = true }\n'
    return f"""[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{spec.name}"
version = "{version}"
description = "{spec.repo_readme}"
readme = "README.md"
requires-python = ">=3.10"
license = "Apache-2.0"
authors = [{{ name = "urisys contributors" }}, {{ name = "Tom Sapletta", email = "tom@sapletta.com" }}]
keywords = ["uri", "urisys", "{spec.name}"]
dependencies = [{deps_str}]
{optional_block}
[tool.uv.sources]
uricore = {{ path = "../uricore", editable = true }}{uv_extra}
{setuptools}
{package_data}
[tool.pytest.ini_options]
testpaths = ["tests"]
"""


def init_repo(spec: PackSpec, *, force: bool = False) -> None:
    if spec.repo.exists() and not force:
        if (spec.repo / "pyproject.toml").is_file():
            print(f"skip init {spec.name}: repo exists at {spec.repo}")
            return
    spec.repo.mkdir(parents=True, exist_ok=True)
    if spec.layout != "flat":
        (spec.repo / spec.name).mkdir(parents=True, exist_ok=True)
    (spec.repo / "tests").mkdir(parents=True, exist_ok=True)
    if not (spec.repo / "pyproject.toml").is_file():
        (spec.repo / "pyproject.toml").write_text(_repo_pyproject(spec), encoding="utf-8")
    if not (spec.repo / "README.md").is_file():
        (spec.repo / "README.md").write_text(
            f"# {spec.name}\n\n{spec.repo_readme}\n\nLicensed under Apache-2.0.\n",
            encoding="utf-8",
        )
    license_src = TELLMESH / "uriocr" / "LICENSE"
    if license_src.is_file() and not (spec.repo / "LICENSE").is_file():
        shutil.copy2(license_src, spec.repo / "LICENSE")
    gitignore_src = TELLMESH / "uriocr" / ".gitignore"
    if gitignore_src.is_file() and not (spec.repo / ".gitignore").is_file():
        shutil.copy2(gitignore_src, spec.repo / ".gitignore")
    test_path = spec.repo / "tests" / f"test_import_{spec.name}.py"
    if not test_path.is_file():
        test_path.write_text(
            f'def test_import_{spec.name}():\n'
            f"    import {spec.name}\n"
            f'    assert {spec.name}.__name__ == "{spec.name}"\n',
            encoding="utf-8",
        )
    sync_to_repo(spec, dry_run=False, tests=True)
    print(f"initialized {spec.name} at {spec.repo}")


def promote(spec: PackSpec, *, dry_run: bool = False) -> None:
    sync_to_repo(spec, dry_run=dry_run, tests=True)
    remove_vendored(spec, dry_run=dry_run)


def _validate_packs(names: list[str], specs: dict[str, PackSpec]) -> bool:
    for name in names:
        if name not in specs:
            print(f"unknown pack: {name}", file=sys.stderr)
            return False
    return True


def _cmd_to_repo(names: list[str], specs: dict[str, PackSpec], args: argparse.Namespace) -> int:
    for name in names:
        if name not in specs:
            print(f"unknown pack: {name}", file=sys.stderr)
            return 2
        changed = sync_to_repo(specs[name], dry_run=args.dry_run, tests=not args.no_tests)
        if changed:
            print(f"{name}: synced {len(changed)} file(s)")
            for item in changed:
                print(f"  - {item}")
        else:
            print(f"{name}: already up to date")
    return 0


def _cmd_promote(names: list[str], specs: dict[str, PackSpec], args: argparse.Namespace) -> int:
    for name in names:
        if name not in specs:
            print(f"unknown pack: {name}", file=sys.stderr)
            return 2
        promote(specs[name], dry_run=args.dry_run)
        print(f"{name}: promoted → {specs[name].repo}")
    return 0


def _cmd_check(names: list[str], specs: dict[str, PackSpec], args: argparse.Namespace) -> int:
    drifts: list[str] = []
    for name in names:
        if name not in specs:
            print(f"unknown pack: {name}", file=sys.stderr)
            return 2
        drifts.extend(check_drift(specs[name]))
    if drifts:
        print("DRIFT:")
        for line in drifts:
            print(f"  {line}")
        return 1
    print(f"OK: {len(names)} pack(s) in sync")
    return 0


def _cmd_init_repo(names: list[str], specs: dict[str, PackSpec], args: argparse.Namespace) -> int:
    for name in names:
        if name not in specs:
            print(f"unknown pack: {name}", file=sys.stderr)
            return 2
        init_repo(specs[name], force=args.force)
    return 0


def _cmd_print_uv_sources(names: list[str], specs: dict[str, PackSpec], args: argparse.Namespace) -> int:
    for name in names:
        if name in SIBLING_ONLY or name in specs:
            print(f'{name} = {{ path = "{sibling_uv_path(name)}", editable = true }}')
    return 0


_COMMAND_HANDLERS: dict[str, Any] = {
    "to-repo": _cmd_to_repo,
    "promote": _cmd_promote,
    "check": _cmd_check,
    "init-repo": _cmd_init_repo,
    "print-uv-sources": _cmd_print_uv_sources,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync urisys packs ↔ tellmesh sibling repos")
    sub = parser.add_subparsers(dest="cmd", required=True)

    for cmd_name, help_text in (
        ("to-repo", "Copy vendored → tellmesh repo"),
        ("check", "Report drift or promote status"),
        ("promote", "to-repo then remove vendored copy"),
    ):
        p = sub.add_parser(cmd_name, help=help_text)
        p.add_argument("packs", nargs="*", default=[])
        p.add_argument("--all", action="store_true")
        if cmd_name != "check":
            p.add_argument("--dry-run", action="store_true")
        if cmd_name == "to-repo":
            p.add_argument("--no-tests", action="store_true")

    p_init = sub.add_parser("init-repo", help="Scaffold tellmesh repo from vendored copy")
    p_init.add_argument("packs", nargs="+")
    p_init.add_argument("--force", action="store_true")

    p_uv = sub.add_parser("print-uv-sources", help="Print [tool.uv.sources] snippet for promoted packs")
    p_uv.add_argument("packs", nargs="*", default=[])
    p_uv.add_argument("--all", action="store_true")

    args = parser.parse_args(argv)
    specs = pack_specs()
    names = list(specs.keys()) if getattr(args, "all", False) else (args.packs or [])
    if not names and args.cmd not in ("init-repo",):
        parser.error("specify pack names or --all")

    handler = _COMMAND_HANDLERS.get(args.cmd)
    if handler is None:
        return 1
    return handler(names, specs, args)


if __name__ == "__main__":
    raise SystemExit(main())
