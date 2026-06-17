#!/usr/bin/env python3
"""Sync vendored capability packs between urisys monorepo and tellmesh/* repos.

Canonical flow (default): monorepo vendored → tellmesh/{pack}/{pack}/

Usage:
  python3 scripts/pack_sync.py to-repo urihim urillm
  python3 scripts/pack_sync.py to-repo --all
  python3 scripts/pack_sync.py check --all
  python3 scripts/pack_sync.py init-repo urimail
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent

MODULE_FILES = ("__init__.py", "handlers.py", "routes.py", "manifest.yaml")

KVM_PACKS = (
    "urikvm",
    "urihim",
    "uriocr",
    "urillm",
    "urimail",
    "urioffice",
    "urivql",
)

OFFICE_PACKS = ("urimail", "urioffice", "urivql")

PACK_TESTS: dict[str, list[str]] = {
    "urihim": ["test_him_driver.py", "test_him_scroll.py"],
    "urillm": ["test_llm_plan.py", "test_vision_dispatch.py"],
    "uriocr": ["test_ocr_llm.py"],
    "urikvm": ["test_kvm.py"],
    "urimail": [],
    "urioffice": [],
    "urivql": [],
}


@dataclass
class PackSpec:
    name: str
    vendored: Path
    repo: Path
    module_files: tuple[str, ...] = MODULE_FILES
    test_files: tuple[str, ...] = ()
    optional_extras: dict[str, list[str]] = field(default_factory=dict)
    repo_readme: str = ""


def _vendored_kvm(name: str) -> Path:
    return ROOT / "urikvm-docker" / "packages" / "python" / name


def _repo(name: str) -> Path:
    return TELLMESH / name


def pack_specs() -> dict[str, PackSpec]:
    specs: dict[str, PackSpec] = {
        "urisysedge": PackSpec(
            name="urisysedge",
            vendored=ROOT / "packages" / "python" / "urisysedge",
            repo=_repo("urisysedge"),
            module_files=("__init__.py", "runtime.py", "env.py"),
            test_files=(),
            repo_readme="Shared URI edge runtime for urisys capability packs.",
        ),
    }
    for name in KVM_PACKS:
        extras: dict[str, list[str]] = {}
        if name == "urihim":
            extras["real"] = ["pyautogui>=0.9.54"]
        elif name == "uriocr":
            extras["real"] = ["pytesseract>=0.3.10", "Pillow>=10.0"]
        elif name == "urillm":
            extras["vision"] = ["litellm>=1.40"]
        elif name == "urioffice":
            extras["writer"] = ["python-docx>=1.1.0"]
        specs[name] = PackSpec(
            name=name,
            vendored=_vendored_kvm(name),
            repo=_repo(name),
            test_files=tuple(PACK_TESTS.get(name, ())),
            optional_extras=extras,
            repo_readme=f"{name}:// URI capability pack for urisys-node.",
        )
    return specs


def read_version(vendored: Path) -> str:
    data = tomllib.loads((vendored / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"]).strip()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_module_dir(spec: PackSpec) -> Path:
    return spec.repo / spec.name


def vendored_module_dir(spec: PackSpec) -> Path:
    return spec.vendored


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
            version_path.write_text(f"{version}\n", encoding="utf-8")
        changed.append(f"{spec.name}/VERSION")

    if tests and spec.test_files:
        tests_dst = spec.repo / "tests"
        tests_src = ROOT / "urikvm-docker" / "tests"
        for test_name in spec.test_files:
            src = tests_src / test_name
            if sync_file(src, tests_dst / test_name, dry_run=dry_run):
                changed.append(f"{spec.name}/tests/{test_name}")

    return changed


def check_drift(spec: PackSpec) -> list[str]:
    if not spec.repo.is_dir():
        return [f"{spec.name}: repo missing at {spec.repo}"]
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


def _repo_pyproject(spec: PackSpec) -> str:
    version = read_version(spec.vendored)
    extras_lines = []
    for extra_name, deps in spec.optional_extras.items():
        dep_str = ", ".join(f'"{d}"' for d in deps)
        extras_lines.append(f'{extra_name} = [{dep_str}]')
    optional_block = ""
    if extras_lines:
        optional_block = "\n[project.optional-dependencies]\n" + "\n".join(extras_lines) + "\ndev = [\"pytest>=8.0\", \"goal>=2.1.0\"]\n"
    package_data = ""
    if (spec.vendored / "manifest.yaml").is_file():
        package_data = f'\n[tool.setuptools.package-data]\n{spec.name} = ["manifest.yaml"]\n'
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
dependencies = ["urisysedge>=0.1.0"]
{optional_block}
[tool.uv.sources]
urisysedge = {{ path = "../urisysedge", editable = true }}

[tool.setuptools.packages.find]
where = ["."]
include = ["{spec.name}*"]
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
    (spec.repo / spec.name).mkdir(parents=True, exist_ok=True)
    (spec.repo / "tests").mkdir(parents=True, exist_ok=True)
    (spec.repo / "pyproject.toml").write_text(_repo_pyproject(spec), encoding="utf-8")
    (spec.repo / "README.md").write_text(
        f"# {spec.name}\n\n{spec.repo_readme}\n\nLicensed under Apache-2.0.\n",
        encoding="utf-8",
    )
    license_src = TELLMESH / "uriocr" / "LICENSE"
    if license_src.is_file():
        shutil.copy2(license_src, spec.repo / "LICENSE")
    gitignore_src = TELLMESH / "uriocr" / ".gitignore"
    if gitignore_src.is_file():
        shutil.copy2(gitignore_src, spec.repo / ".gitignore")
    goal_src = TELLMESH / "uriocr" / "goal.yaml"
    if goal_src.is_file() and not (spec.repo / "goal.yaml").is_file():
        text = goal_src.read_text(encoding="utf-8")
        text = re.sub(r"name: uriocr", f"name: {spec.name}", text)
        text = re.sub(r"scope: uriocr", f"scope: {spec.name}", text)
        text = re.sub(r"dist/uriocr-", f"dist/{spec.name}-", text)
        (spec.repo / "goal.yaml").write_text(text, encoding="utf-8")
    test_path = spec.repo / "tests" / "test_import.py"
    if not test_path.is_file():
        test_path.write_text(
            f'def test_import_{spec.name}():\n'
            f"    import {spec.name}\n"
            f'    assert {spec.name}.__name__ == "{spec.name}"\n',
            encoding="utf-8",
        )
    sync_to_repo(spec, dry_run=False, tests=True)
    print(f"initialized {spec.name} at {spec.repo}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync urisys vendored packs ↔ tellmesh repos")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_to = sub.add_parser("to-repo", help="Copy monorepo vendored → tellmesh repo")
    p_to.add_argument("packs", nargs="*", default=[])
    p_to.add_argument("--all", action="store_true")
    p_to.add_argument("--dry-run", action="store_true")
    p_to.add_argument("--no-tests", action="store_true")

    p_check = sub.add_parser("check", help="Report drift without copying")
    p_check.add_argument("packs", nargs="*", default=[])
    p_check.add_argument("--all", action="store_true")

    p_init = sub.add_parser("init-repo", help="Scaffold tellmesh repo from urihim template")
    p_init.add_argument("packs", nargs="+")
    p_init.add_argument("--force", action="store_true")

    args = parser.parse_args(argv)
    specs = pack_specs()
    names = list(specs.keys()) if getattr(args, "all", False) else (args.packs or [])
    if not names and args.cmd != "init-repo":
        parser.error("specify pack names or --all")

    if args.cmd == "to-repo":
        total: list[str] = []
        for name in names:
            if name not in specs:
                print(f"unknown pack: {name}", file=sys.stderr)
                return 2
            changed = sync_to_repo(
                specs[name],
                dry_run=args.dry_run,
                tests=not args.no_tests,
            )
            if changed:
                print(f"{name}: synced {len(changed)} file(s)")
                for item in changed:
                    print(f"  - {item}")
            else:
                print(f"{name}: already up to date")
            total.extend(changed)
        return 0

    if args.cmd == "check":
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

    if args.cmd == "init-repo":
        for name in args.packs:
            if name not in specs:
                print(f"unknown pack: {name}", file=sys.stderr)
                return 2
            init_repo(specs[name], force=args.force)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
