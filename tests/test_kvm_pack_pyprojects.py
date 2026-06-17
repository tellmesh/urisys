"""PyPI-ready layout for kvm/him/ocr/llm capability packs (tellmesh sibling repos)."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent
PACKS = ("urikvm", "urihim", "uriocr", "urillm", "urimail", "urioffice", "urivql")
OFFICE_PACKS = ("urimail", "urioffice", "urivql")


def _name(path: Path) -> str:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data["project"]["name"]


def test_urisysedge_sibling_pyproject():
    path = TELLMESH / "urisysedge" / "pyproject.toml"
    assert path.is_file()
    assert _name(path) == "urisysedge"


def test_each_kvm_pack_has_sibling_pyproject():
    for pkg in PACKS:
        path = TELLMESH / pkg / "pyproject.toml"
        assert path.is_file(), f"missing {path}"
        assert _name(path) == pkg


def test_sibling_pack_pyprojects_depend_on_urisysedge():
    for pkg in PACKS:
        path = TELLMESH / pkg / "pyproject.toml"
        deps = tomllib.loads(path.read_text(encoding="utf-8"))["project"]["dependencies"]
        assert any(d.startswith("urisysedge>=") for d in deps), pkg


def test_urillm_imports_urisysedge_not_urikvmedge():
    handlers = TELLMESH / "urillm" / "urillm" / "handlers.py"
    if not handlers.is_file():
        handlers = TELLMESH / "urillm" / "handlers.py"
    src = handlers.read_text(encoding="utf-8")
    assert "urisysedge.env" in src
    assert "urikvmedge" not in src


def test_urisys_root_uv_sources_point_to_siblings():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    sources = data["tool"]["uv"]["sources"]
    for pkg in ("urisysedge", "urioperators", *PACKS):
        rel = sources[pkg]["path"]
        assert rel.startswith("../"), f"{pkg} should use sibling path, got {rel}"
        assert (TELLMESH / pkg).is_dir(), f"missing sibling repo {pkg}"


def test_vendored_kvm_pack_dirs_removed():
    for pkg in PACKS:
        vendored = TELLMESH / "urikvm-docker" / "packages" / "python" / pkg
        assert not vendored.is_dir(), f"vendored copy still present: {vendored}"


def test_urikvmedge_promoted_to_sibling():
    path = TELLMESH / "urikvmedge" / "pyproject.toml"
    assert path.is_file()
    assert _name(path) == "urikvmedge"
    vendored = TELLMESH / "urikvm-docker" / "packages" / "python" / "urikvmedge"
    assert not vendored.is_dir(), f"vendored copy still present: {vendored}"
