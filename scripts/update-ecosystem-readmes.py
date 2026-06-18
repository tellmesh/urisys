#!/usr/bin/env python3
"""Inject or replace ## Ekosystem TellMesh section in package README.md files."""

from __future__ import annotations

import re
from pathlib import Path

TELLMESH = Path(__file__).resolve().parents[2]
MESH = "https://github.com/tellmesh/urisys/blob/main/docs/MESH.md"
ECOSYSTEM = "https://github.com/tellmesh/urisys/blob/main/../docs/ECOSYSTEM.md"

MARKER_START = "## Ekosystem TellMesh"
MARKER_END = "<!-- end-ecosystem -->"

# (repo_dir_name, table rows as markdown lines inside section)
PACKAGES: dict[str, list[str]] = {
    "urisys": [
        "| **Warstwa** | Orchestrator (centrum mesh) |",
        "| **Moduł** | `urisys` |",
        "| **Zależności** | `uricontrol`, `uriresolver` |",
        "| **Rola** | CLI, Markpact, flow runner, PackManager, `urisys init` |",
    ],
    "uricontrol": [
        "| **Warstwa** | Control plane + edge runtime |",
        "| **Moduł** | `uri_control`, `uri_control.edge` |",
        "| **Zależności** | `uriguard` |",
        "| **Rola** | CapabilityRegistry, policy, handlers, `Runtime`, `compose`, `http.serve` |",
        "| **Uwaga** | Zastępuje legacy PyPI `uricore` i `urisysedge` (usunięty 2026-06) |",
    ],
    "uriguard": [
        "| **Warstwa** | Policy gate |",
        "| **Moduł** | `uri_guard` |",
        "| **Orchestrator** | [urisys](https://github.com/tellmesh/urisys) |",
        "| **Rola** | Shell allowlist, limits, risk gate (uricontrol dependency) |",
    ],
    "uriresolver": [
        "| **Warstwa** | Intent resolver (GDZIE) |",
        "| **Moduł** | `uri_resolver` |",
        "| **Orchestrator** | [urisys](https://github.com/tellmesh/urisys) |",
        "| **Rola** | Resolver YAML, uri_aliases, target selection |",
    ],
    "urisys-node": [
        "| **Warstwa** | Slave / edge node |",
        "| **Moduł** | `urisysnode` |",
        "| **Orchestrator** | [urisys](https://github.com/tellmesh/urisys) |",
        "| **Runtime** | `uri_control.edge` via `uricontrol` |",
        "| **Port** | 8790 |",
        "| **Rola** | screen/shell + lazy hot-load packów (kvm, him, …) |",
    ],
    "urioperators": [
        "| **Warstwa** | Shared library (LLM) |",
        "| **Moduł** | `urioperators` |",
        "| **Używane przez** | `urillm`, packi vision |",
        "| **Rola** | `llm_chat`, `llm_plan`, `parse_json_response` |",
    ],
    "markpact-contracts": [
        "| **Warstwa** | Kontrakty / przykłady |",
        "| **Orchestrator** | [urisys](https://github.com/tellmesh/urisys) |",
        "| **Rola** | Markpact packs, resolver examples, transport binding |",
    ],
    "markpact-pololu": [
        "| **Warstwa** | Device reference (Pololu Tic T249) |",
        "| **Scheme** | `stepper://` |",
        "| **Orchestrator** | [urisys](https://github.com/tellmesh/urisys) |",
        "| **Router** | [uriresolver](https://github.com/tellmesh/uriresolver) + `profiles/urisys.runtime.*.yaml` |",
        "| **Runtime** | `uritic-host` (Go), ESP32 firmware |",
    ],
    # capability packs
    "urikvm": ["| **Warstwa** | Capability pack |", "| **Scheme** | `kvm://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | [urikvmedge](https://github.com/tellmesh/urikvmedge), urikvm-docker |", "| **Port** | 8794 |"],
    "urihim": ["| **Warstwa** | Capability pack |", "| **Scheme** | `him://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urikvmedge, urirdpedge |"],
    "uriocr": ["| **Warstwa** | Capability pack |", "| **Scheme** | `ocr://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urikvmedge |"],
    "urillm": ["| **Warstwa** | Capability pack |", "| **Scheme** | `llm://` |", "| **Zależność** | `uricontrol>=0.1.8`, `urioperators` |", "| **Edge** | urikvmedge |"],
    "urimail": ["| **Warstwa** | Capability pack |", "| **Scheme** | `urimail://` |", "| **Zależność** | `uricontrol>=0.1.8` |"],
    "urioffice": ["| **Warstwa** | Capability pack |", "| **Scheme** | `urioffice://` |", "| **Zależność** | `uricontrol>=0.1.8` |"],
    "urivql": ["| **Warstwa** | Capability pack |", "| **Scheme** | `vql://` |", "| **Zależność** | `uricontrol>=0.1.8` |"],
    "uristepper": ["| **Warstwa** | Capability pack |", "| **Scheme** | `stepper://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Runtime** | `uri_control.edge.Runtime` |", "| **Edge** | uristepperedge, markpact-pololu |"],
    "uriscreen": ["| **Warstwa** | Capability pack |", "| **Scheme** | `screen://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urisys-node |"],
    "urishell": ["| **Warstwa** | Capability pack |", "| **Scheme** | `shell://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urisys-node, urirdpedge |"],
    "uribrowser": ["| **Warstwa** | Capability pack |", "| **Scheme** | `browser://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | uribrowser-docker |", "| **Port** | 8797 |"],
    "urienv": ["| **Warstwa** | Capability pack |", "| **Scheme** | `env://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urienv-docker |"],
    "urichat": ["| **Warstwa** | Capability pack (deprecated) |", "| **Scheme** | `chat://` |", "| **Zależność** | `uricontrol>=0.1.8` |"],
    "urimessage": ["| **Warstwa** | Capability pack |", "| **Scheme** | `message://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urisys-automation-lab |"],
    "uriwebrtc": ["| **Warstwa** | Capability pack |", "| **Scheme** | `webrtc://` |", "| **Zależność** | `uricontrol>=0.1.8` |"],
    "uristt": ["| **Warstwa** | Capability pack |", "| **Scheme** | `stt://` / `tts://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urisys-automation-lab |"],
    "uriimg2nl": ["| **Warstwa** | Capability pack |", "| **Scheme** | `img2nl://` |", "| **Zależność** | `uricontrol>=0.1.8` |"],
    "urikv": ["| **Warstwa** | Capability pack |", "| **Scheme** | `kv://` / `log://` |", "| **Zależność** | `uricontrol>=0.1.8` |"],
    "urirdp": ["| **Warstwa** | Capability pack |", "| **Scheme** | `rdp://` |", "| **Zależność** | `uricontrol>=0.1.8` |", "| **Edge** | urirdpedge |", "| **Port** | 8795 |"],
    # edge CLIs
    "urirdpedge": ["| **Warstwa** | Edge CLI |", "| **CLI** | `urisys-rdp` |", "| **Runtime** | `uri_control.edge` (`uricontrol`) |", "| **Packi** | urirdp, urikvm, urihim, urishell, uribrowser, … |", "| **Port** | 8795 |"],
    "urikvmedge": ["| **Warstwa** | Edge CLI |", "| **CLI** | `urisys-kvm` |", "| **Runtime** | `uri_control.edge` (`uricontrol`) |", "| **Packi** | urikvm, urihim, uriocr, urillm |", "| **Port** | 8794 |"],
    "uristepperedge": ["| **Warstwa** | Edge CLI |", "| **Runtime** | `uri_control.edge` (`uricontrol`) |", "| **Pack** | uristepper |", "| **Port** | 8791 |"],
    # docker glue (in urisys tree or sibling)
    "urikvm-docker": ["| **Warstwa** | Docker glue |", "| **Obraz** | kvm/him/ocr/llm bundle |", "| **Build** | `docker build -f urikvm-docker/Dockerfile tellmesh/` |", "| **Zależności** | uriresolver, uriguard, uricontrol, urikvmedge |"],
    "urirdp-docker": ["| **Warstwa** | Docker glue |", "| **Obraz** | RDP desktop automation |", "| **Zależności** | uriresolver, uriguard, uricontrol, urirdpedge |"],
    "uribrowser-docker": ["| **Warstwa** | Docker glue |", "| **Scheme** | `browser://` |", "| **Zależności** | uriresolver, uriguard, uricontrol |"],
    "urienv-docker": ["| **Warstwa** | Docker glue |", "| **Scheme** | `env://` |", "| **Zależność** | uricontrol (`uri_control`) |"],
    "uristepper-docker": ["| **Warstwa** | Docker glue |", "| **Scheme** | `stepper://` |", "| **Zależności** | uriresolver, uriguard, uricontrol, uristepperedge |"],
    "urisys-automation-lab": ["| **Warstwa** | Lab / voice gateway |", "| **Port** | 8099 |", "| **Schemes** | stt, webrtc, message |", "| **Orchestrator** | urisys |"],
}


def build_section(rows: list[str]) -> str:
    common = [
        MARKER_START,
        "",
        "Orchestrator: **[urisys](https://github.com/tellmesh/urisys)** · Mapa: **[MESH.md](%s)** · Model: **[ECOSYSTEM.md](https://github.com/tellmesh/urisys/blob/main/docs/ECOSYSTEM.md)**"
        % MESH,
        "",
        "| Pole | Wartość |",
        "|------|---------|",
        *rows,
        "",
        "Runtime edge: **`uri_control.edge`** w pakiecie **`uricontrol`** (legacy PyPI `uricore` / `urisysedge` usunięty 2026-06).",
        "Resolver intencji: **`uriresolver`** (`uri_resolver`) + transport w **`uritransport`**; policy gate: **`uriguard`** (`uri_guard`).",
        "",
        MARKER_END,
        "",
    ]
    return "\n".join(common)


def strip_old_section(text: str) -> str:
    if MARKER_START in text:
        return re.sub(
            rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}\n*",
            "",
            text,
            flags=re.DOTALL,
        )
    return text


def fix_urisysedge_refs(text: str) -> str:
    repl = [
        ("`uri_control.edge`.Runtime", "`uri_control.edge.Runtime`"),
        ("urisysedge.Runtime", "`uri_control.edge.Runtime`"),
        ("urisysedge", "`uricontrol` (`uri_control.edge`)"),
        ("`uricontrol` (`uri_control.edge`)>=0.1.0", "`uricontrol>=0.1.8`"),
        ("packages/python/urisysedge", "uricontrol/core/python/uri_control/edge"),
        ("tellmesh/urisysedge", "tellmesh/uricontrol"),
        ("tellmesh/uricore", "tellmesh/uricontrol"),
        ("../uricore/", "../uricontrol/"),
    ]
    for a, b in repl:
        text = text.replace(a, b)
    return text


def main() -> None:
    updated = 0
    for name, rows in PACKAGES.items():
        readme = TELLMESH / name / "README.md"
        if not readme.is_file():
            continue
        text = readme.read_text(encoding="utf-8")
        text = fix_urisysedge_refs(text)
        text = strip_old_section(text)
        section = build_section(rows)
        # Insert before ## License if present, else append
        if "\n## License" in text:
            text = text.replace("\n## License", f"\n{section}\n## License", 1)
        else:
            text = text.rstrip() + "\n\n" + section
        readme.write_text(text, encoding="utf-8")
        updated += 1
        print("updated", name)
    print(f"Done: {updated} README files")


if __name__ == "__main__":
    main()
