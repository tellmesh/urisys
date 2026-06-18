"""Registry: capability pack → tellmesh sibling repo (single source of truth).

After migration, urisys monorepo holds only docker glue (*-docker, configs).
Pack code lives in /home/tom/github/tellmesh/{repo}/.

Usage:
  from scripts.pack_registry import sibling_repo, sibling_uv_path, pack_specs
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent

MODULE_FILES = ("__init__.py", "handlers.py", "routes.py", "manifest.yaml")
EDGE_FILES = ("__init__.py", "runtime.py", "cli.py", "__main__.py")


@dataclass
class PackSpec:
    name: str
    repo: Path
    vendored: Path | None
    module_files: tuple[str, ...] = MODULE_FILES
    test_files: tuple[str, ...] = ()
    optional_extras: dict[str, list[str]] = field(default_factory=dict)
    repo_readme: str = ""
    layout: str = "nested"  # nested: repo/{name}/; flat: repo root is the package
    extra_deps: tuple[str, ...] = ()  # extra pip deps for repo pyproject
    module_dir: str | None = None  # override module path under repo (e.g. "core/python/uri_control/edge")


def _repo(name: str) -> Path:
    return TELLMESH / name


def sibling_uv_path(name: str) -> str:
    """Relative path for [tool.uv.sources] from urisys root."""
    return f"../{name}"


def sibling_repo(name: str) -> Path:
    return _repo(name)


def _pack(
    name: str,
    *,
    repo: str | None = None,
    vendored: Path | None = None,
    module_files: tuple[str, ...] = MODULE_FILES,
    test_files: tuple[str, ...] = (),
    optional_extras: dict[str, list[str]] | None = None,
    repo_readme: str = "",
    layout: str = "nested",
    extra_deps: tuple[str, ...] = (),
    module_dir: str | None = None,
) -> PackSpec:
    return PackSpec(
        name=name,
        repo=_repo(repo or name),
        vendored=vendored,
        module_files=module_files,
        test_files=test_files,
        optional_extras=optional_extras or {},
        repo_readme=repo_readme,
        layout=layout,
        extra_deps=extra_deps,
        module_dir=module_dir,
    )


def pack_specs() -> dict[str, PackSpec]:
    specs: dict[str, PackSpec] = {}

    specs["uricontrol"] = _pack(
        "uricontrol",
        module_dir="core/python/uri_control/edge",
        module_files=("__init__.py", "runtime.py", "env.py"),
        repo_readme="Shared URI edge runtime for urisys capability packs.",
    )
    specs["urioperators"] = _pack(
        "urioperators",
        module_files=("__init__.py", "llm_json.py", "llm_chat.py", "llm_plan.py", "llm_decide.py"),
        test_files=("test_llm_helpers.py",),
        repo_readme="Shared LLM operator helpers for urikvm and urirdp packs.",
        layout="flat",
    )

    kvm_tests: dict[str, list[str]] = {
        "urihim": ["test_him_driver.py", "test_him_scroll.py"],
        "urillm": ["test_llm_plan.py", "test_vision_dispatch.py"],
        "uriocr": ["test_ocr_llm.py"],
        "urikvm": ["test_kvm.py"],
    }
    kvm_extras: dict[str, dict[str, list[str]]] = {
        "urihim": {"real": ["pyautogui>=0.9.54"]},
        "uriocr": {"real": ["pytesseract>=0.3.10", "Pillow>=10.0"]},
        "urillm": {"vision": ["litellm>=1.40"]},
        "urioffice": {"writer": ["python-docx>=1.1.0"]},
    }
    kvm_extra_deps: dict[str, tuple[str, ...]] = {
        "urillm": ("urioperators>=0.1.0",),
    }

    for name in ("urikvm", "urihim", "uriocr", "urillm", "urimail", "urioffice", "urivql"):
        specs[name] = _pack(
            name,
            test_files=tuple(kvm_tests.get(name, ())),
            optional_extras=kvm_extras.get(name, {}),
            extra_deps=kvm_extra_deps.get(name, ()),
            repo_readme=f"{name}:// URI capability pack.",
        )

    specs["urikvmedge"] = _pack(
        "urikvmedge",
        module_files=EDGE_FILES,
        repo_readme="KVM edge CLI (urisys-kvm) — composes urikvm/him/ocr/llm packs.",
    )

    specs["uriscreen"] = _pack(
        "uriscreen",
        module_files=("__init__.py", "handlers.py", "routes.py", "backends.py", "portal_capture.py", "manifest.yaml"),
        repo_readme="screen:// URI capability pack.",
    )

    specs["urisysnode"] = _pack(
        "urisysnode",
        repo="urisys-node",
        module_files=(
            "__init__.py",
            "cli.py",
            "serve.py",
            "handlers.py",
            "routes.py",
            "runtime.py",
            "env.py",
            "forward.py",
            "forward_config.py",
            "artifact_resolver.py",
            "pack_resolver.py",
            "release_verify.py",
            "identity.py",
            "router.py",
            "client.py",
            "display_bootstrap.py",
            "manifest.yaml",
        ),
        repo_readme="urisys-node slave URI server runtime.",
    )

    specs["urishell"] = _pack(
        "urishell",
        repo_readme="shell:// URI capability pack.",
    )

    specs["urirdp"] = _pack(
        "urirdp",
        module_files=("__init__.py", "handlers.py", "routes.py", "manifest.yaml", "display.py"),
        repo_readme="rdp:// URI capability pack.",
    )
    specs["urirdpedge"] = _pack(
        "urirdpedge",
        module_files=EDGE_FILES + ("lab_browser.py",),
        repo_readme="RDP edge CLI (urisys-rdp) — composes desktop automation packs.",
    )

    for name in ("uribrowserdocker", "uribrowseredge"):
        specs[name] = _pack(
            name,
            repo="uribrowser",
            module_files=EDGE_FILES if "edge" in name else MODULE_FILES,
            repo_readme="browser:// URI capability pack.",
        )

    specs["urienv"] = _pack(
        "urienv",
        module_files=("__init__.py", "handlers.py", "routes.py", "manifest.yaml"),
        repo_readme="env:// URI capability pack.",
        layout="flat",
    )

    specs["urikv"] = _pack(
        "urikv",
        repo_readme="kv:// and log:// URI packs — shared state and system introspection.",
    )

    specs["uristepper"] = _pack(
        "uristepper",
        repo_readme="stepper:// URI capability pack.",
    )
    specs["uristepperedge"] = _pack(
        "uristepperedge",
        module_files=EDGE_FILES,
        repo_readme="Stepper edge CLI — composes uristepper pack.",
    )

    for name in ("labedge",):
        specs[name] = _pack(
            name,
            repo="urisys-automation-lab",
            module_files=EDGE_FILES if name == "labedge" else MODULE_FILES,
            repo_readme="urisys automation lab MVP packs.",
        )

    for name in ("urimessage", "uristt", "uriwebrtc", "urichat"):
        specs[name] = _pack(
            name,
            repo_readme=f"{name}:// URI capability pack for automation lab.",
        )

    return specs


# Packs with standalone tellmesh repos (canonical, no vendored copy in urisys)
SIBLING_ONLY = frozenset(
    {
        "uricontrol",
        "urioperators",
        "urikvm",
        "urihim",
        "uriocr",
        "urillm",
        "urimail",
        "urioffice",
        "urivql",
        "urikvmedge",
        "urienv",
        "urikv",
        "urishell",
        "uriscreen",
        "urirdp",
        "urirdpedge",
        "uristepperedge",
        "urimessage",
        "uristt",
        "uriwebrtc",
        "urichat",
    }
)

# Multi-module repos (several pack names → one git repo)
BUNDLE_REPOS: dict[str, str] = {
    "urisysnode": "urisys-node",
    "uribrowserdocker": "uribrowser",
    "uribrowseredge": "uribrowser",
    "uristepper": "uristepper",
    "labedge": "urisys-automation-lab",
}


def sibling_repo_names() -> frozenset[str]:
    """Unique tellmesh repo directory names for all promoted packs."""
    return frozenset(SIBLING_ONLY | frozenset(BUNDLE_REPOS.values()))


def all_promoted_packs() -> frozenset[str]:
    return frozenset(pack_specs().keys())
