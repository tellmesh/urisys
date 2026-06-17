"""PyPI-ready layout for kvm/him/ocr/llm capability packs (vendored in monorepo)."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "packages" / "python" / "urisysedge" / "pyproject.toml"
PACKS = ("urikvm", "urihim", "uriocr", "urillm", "urimail", "urioffice", "urivql")


def _name(path: Path) -> str:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data["project"]["name"]


def test_urisysedge_pyproject():
    assert EDGE.is_file()
    assert _name(EDGE) == "urisysedge"


def test_each_pack_has_own_pyproject():
    for pkg in PACKS:
        path = ROOT / "urikvm-docker" / "packages" / "python" / pkg / "pyproject.toml"
        assert path.is_file(), f"missing {path}"
        assert _name(path) == pkg


def test_pack_pyprojects_depend_on_urisysedge():
    for pkg in PACKS:
        path = ROOT / "urikvm-docker" / "packages" / "python" / pkg / "pyproject.toml"
        deps = tomllib.loads(path.read_text(encoding="utf-8"))["project"]["dependencies"]
        assert any(d.startswith("urisysedge>=") for d in deps), pkg


def test_urillm_imports_urisysedge_not_urikvmedge():
    src = (ROOT / "urikvm-docker" / "packages" / "python" / "urillm" / "handlers.py").read_text(
        encoding="utf-8"
    )
    assert "urisysedge.env" in src
    assert "urikvmedge" not in src


def test_urisys_bundles_urisysedge():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    include = data["tool"]["setuptools"]["packages"]["find"]["include"]
    assert any("urisysedge" in item for item in include)


def test_urisys_kvm_optional_uses_local_sources():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    sources = data["tool"]["uv"]["sources"]
    for pkg in PACKS:
        assert pkg in sources, pkg


def test_urisys_node_kvm_optional_deps():
    path = ROOT / "urisys-node" / "pyproject.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    assert any(d.startswith("urisysedge>=") for d in deps)
    kvm = data["project"]["optional-dependencies"]["kvm"]
    assert any("urikvm" in d for d in kvm)
    assert any("urillm" in d for d in kvm)
