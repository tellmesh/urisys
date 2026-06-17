"""Registry: capability pack → tellmesh sibling repo (single source of truth).

After migration, urisys monorepo holds only docker glue (*edge CLIs, configs).
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
EDGE_FILES = ("__init__.py", "runtime.py", "env.py", "cli.py")


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


def _repo(name: str) -> Path:
    return TELLMESH / name


def _vendored_kvm(name: str) -> Path:
    return ROOT / "urikvm-docker" / "packages" / "python" / name


def _vendored_rdp(name: str) -> Path:
    return ROOT / "urirdp-docker" / "packages" / "python" / name


def _vendored_node(name: str) -> Path:
    return ROOT / "urisys-node" / "packages" / "python" / name


def sibling_uv_path(name: str) -> str:
    """Relative path for [tool.uv.sources] from urisys root."""
    return f"../{name}"


def sibling_repo(name: str) -> Path:
    return _repo(name)


def pack_specs() -> dict[str, PackSpec]:
    specs: dict[str, PackSpec] = {
        "urisysedge": PackSpec(
            name="urisysedge",
            repo=_repo("urisysedge"),
            vendored=ROOT / "packages" / "python" / "urisysedge",
            module_files=("__init__.py", "runtime.py", "env.py"),
            repo_readme="Shared URI edge runtime for urisys capability packs.",
            layout="nested",
        ),
        "urioperators": PackSpec(
            name="urioperators",
            repo=_repo("urioperators"),
            vendored=ROOT / "packages" / "python" / "urioperators",
            module_files=("__init__.py", "llm_json.py", "llm_chat.py", "llm_plan.py", "llm_decide.py"),
            test_files=("test_llm_helpers.py",),
            repo_readme="Shared LLM operator helpers for urikvm and urirdp packs.",
            layout="flat",
        ),
    }

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

    for name in (
        "urikvm",
        "urihim",
        "uriocr",
        "urillm",
        "urimail",
        "urioffice",
        "urivql",
    ):
        specs[name] = PackSpec(
            name=name,
            repo=_repo(name),
            vendored=_vendored_kvm(name),
            test_files=tuple(kvm_tests.get(name, ())),
            optional_extras=kvm_extras.get(name, {}),
            extra_deps=kvm_extra_deps.get(name, ()),
            repo_readme=f"{name}:// URI capability pack for urisys-node.",
        )

    specs["urikvmedge"] = PackSpec(
        name="urikvmedge",
        repo=_repo("urikvmedge"),
        vendored=_vendored_kvm("urikvmedge"),
        module_files=EDGE_FILES,
        repo_readme="KVM docker bundle CLI (urisys-kvm) — composes urikvm/him/ocr/llm packs.",
    )

    for name in (
        "urisysnode",
        "uriscreen",
        "urishell",
    ):
        module_files = MODULE_FILES if name != "urisysnode" else ("__init__.py", "cli.py", "serve.py", "handlers.py", "routes.py", "runtime.py", "env.py", "forward.py", "forward_config.py", "artifact_resolver.py", "pack_resolver.py", "release_verify.py", "identity.py", "router.py", "client.py", "display_bootstrap.py")
        if name == "uriscreen":
            module_files = ("__init__.py", "handlers.py", "routes.py", "backends.py")
        if name == "urishell":
            module_files = ("__init__.py", "handlers.py", "routes.py")
        specs[name] = PackSpec(
            name=name,
            repo=_repo("urisys-node"),
            vendored=_vendored_node(name),
            module_files=module_files,
            repo_readme="urisys-node slave: screen/kvm/him URI server components.",
        )

    rdp_packs = (
        "urirdp",
        "urirdp_kvm",
        "urirdp_him",
        "urirdp_ocr",
        "urirdp_llm",
        "urirdp_browser",
        "urirdp_shell",
        "urirdp_env",
        "urirdpedge",
    )
    for name in rdp_packs:
        files = EDGE_FILES if name == "urirdpedge" else MODULE_FILES
        specs[name] = PackSpec(
            name=name,
            repo=_repo("urirdp"),
            vendored=_vendored_rdp(name),
            module_files=files,
            extra_deps=("urioperators>=0.1.0",) if name == "urirdp_llm" else (),
            repo_readme="RDP desktop automation pack bundle for urisys.",
        )

    for name, vendored_base in (
        ("uribrowserdocker", ROOT / "uribrowser-docker" / "packages" / "python" / "uribrowserdocker"),
        ("uribrowseredge", ROOT / "uribrowser-docker" / "packages" / "python" / "uribrowseredge"),
    ):
        specs[name] = PackSpec(
            name=name,
            repo=_repo("uribrowser"),
            vendored=vendored_base,
            module_files=EDGE_FILES if "edge" in name else MODULE_FILES,
            repo_readme="browser:// URI capability pack.",
        )

    specs["urienv"] = PackSpec(
        name="urienv",
        repo=_repo("urienv"),
        vendored=ROOT / "urienv-docker" / "packages" / "python" / "urienv" / "src" / "urienv",
        module_files=("__init__.py",),
        repo_readme="env:// URI capability pack.",
        layout="flat",
    )

    for name in ("uristepper", "uristepperedge"):
        specs[name] = PackSpec(
            name=name,
            repo=_repo("uristepper"),
            vendored=ROOT / "uristepper-docker" / "packages" / "python" / name,
            module_files=EDGE_FILES if name == "uristepperedge" else MODULE_FILES,
            repo_readme="stepper:// URI capability pack.",
        )

    lab_packs = ("labedge", "urimessage", "urichat", "uristt", "uriwebrtc")
    for name in lab_packs:
        specs[name] = PackSpec(
            name=name,
            repo=_repo("urisys-automation-lab"),
            vendored=ROOT / "urisys-automation-lab" / "packages" / "python" / name,
            module_files=EDGE_FILES if name == "labedge" else MODULE_FILES,
            repo_readme="urisys automation lab MVP packs.",
        )

    return specs


# Packs with standalone tellmesh repos (canonical, no vendored copy in urisys)
SIBLING_ONLY = frozenset(
    {
        "urisysedge",
        "urioperators",
        "urikvm",
        "urihim",
        "uriocr",
        "urillm",
        "urimail",
        "urioffice",
        "urivql",
    }
)

# Bundled into multi-module tellmesh repos
BUNDLE_REPOS: dict[str, str] = {
    "urisysnode": "urisys-node",
    "uriscreen": "urisys-node",
    "urishell": "urisys-node",
    "urirdp": "urirdp",
    "urirdp_kvm": "urirdp",
    "urirdp_him": "urirdp",
    "urirdp_ocr": "urirdp",
    "urirdp_llm": "urirdp",
    "urirdp_browser": "urirdp",
    "urirdp_shell": "urirdp",
    "urirdp_env": "urirdp",
    "urirdpedge": "urirdp",
    "uribrowserdocker": "uribrowser",
    "uribrowseredge": "uribrowser",
    "uristepper": "uristepper",
    "uristepperedge": "uristepper",
    "labedge": "urisys-automation-lab",
    "urimessage": "urisys-automation-lab",
    "urichat": "urisys-automation-lab",
    "uristt": "urisys-automation-lab",
    "uriwebrtc": "urisys-automation-lab",
}
