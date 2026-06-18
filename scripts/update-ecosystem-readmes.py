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
        "| **Zależności** | `uricore`, `urirouter` |",
        "| **Rola** | CLI, Markpact, flow runner, PackManager, `urisys init` |",
    ],
    "uricore": [
        "| **Warstwa** | Control plane + edge runtime |",
        "| **Moduł** | `uri_control`, `uri_control.edge` |",
        "| **Zależności** | `urirouter` |",
        "| **Rola** | CapabilityRegistry, policy, handlers, `Runtime`, `compose`, `http.serve` |",
        "| **Uwaga** | Zastępuje legacy `urisysedge` (usunięty 2026-06) |",
    ],
    "urirouter": [
        "| **Warstwa** | Intent router (GDZIE + JAK) |",
        "| **Moduł** | `uri_router` |",
        "| **Orchestrator** | [urisys](https://github.com/tellmesh/urisys) |",
        "| **Rola** | Resolver YAML, HTTP/MQTT delegate, wire envelope |",
    ],
    "urisys-node": [
        "| **Warstwa** | Slave / edge node |",
        "| **Moduł** | `urisysnode` |",
        "| **Orchestrator** | [urisys](https://github.com/tellmesh/urisys) |",
        "| **Runtime** | `uri_control.edge` via `uricore` |",
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
        "| **Router** | [urirouter](https://github.com/tellmesh/urirouter) + `profiles/urisys.runtime.*.yaml` |",
        "| **Runtime** | `uritic-host` (Go), ESP32 firmware |",
    ],
    # capability packs
    "urikvm": ["| **Warstwa** | Capability pack |", "| **Scheme** | `kvm://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | [urikvmedge](https://github.com/tellmesh/urikvmedge), urikvm-docker |", "| **Port** | 8794 |"],
    "urihim": ["| **Warstwa** | Capability pack |", "| **Scheme** | `him://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urikvmedge, urirdpedge |"],
    "uriocr": ["| **Warstwa** | Capability pack |", "| **Scheme** | `ocr://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urikvmedge |"],
    "urillm": ["| **Warstwa** | Capability pack |", "| **Scheme** | `llm://` |", "| **Zależność** | `uricore>=0.1.8`, `urioperators` |", "| **Edge** | urikvmedge |"],
    "urimail": ["| **Warstwa** | Capability pack |", "| **Scheme** | `mail://` |", "| **Zależność** | `uricore>=0.1.8` |"],
    "urioffice": ["| **Warstwa** | Capability pack |", "| **Scheme** | `office://` |", "| **Zależność** | `uricore>=0.1.8` |"],
    "urivql": ["| **Warstwa** | Capability pack |", "| **Scheme** | `vql://` |", "| **Zależność** | `uricore>=0.1.8` |"],
    "uristepper": ["| **Warstwa** | Capability pack |", "| **Scheme** | `stepper://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Runtime** | `uri_control.edge.Runtime` |", "| **Edge** | uristepperedge, markpact-pololu |"],
    "uriscreen": ["| **Warstwa** | Capability pack |", "| **Scheme** | `screen://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urisys-node |"],
    "urishell": ["| **Warstwa** | Capability pack |", "| **Scheme** | `shell://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urisys-node, urirdpedge |"],
    "uribrowser": ["| **Warstwa** | Capability pack |", "| **Scheme** | `browser://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | uribrowser-docker |", "| **Port** | 8797 |"],
    "urienv": ["| **Warstwa** | Capability pack |", "| **Scheme** | `env://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urienv-docker |"],
    "urichat": ["| **Warstwa** | Capability pack (deprecated) |", "| **Scheme** | `chat://` |", "| **Zależność** | `uricore>=0.1.8` |"],
    "urimessage": ["| **Warstwa** | Capability pack |", "| **Scheme** | `message://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urisys-automation-lab |"],
    "uriwebrtc": ["| **Warstwa** | Capability pack |", "| **Scheme** | `webrtc://` |", "| **Zależność** | `uricore>=0.1.8` |"],
    "uristt": ["| **Warstwa** | Capability pack |", "| **Scheme** | `stt://` / `tts://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urisys-automation-lab |"],
    "uriimg2nl": ["| **Warstwa** | Capability pack |", "| **Scheme** | `img2nl://` |", "| **Zależność** | `uricore>=0.1.8` |"],
    "urikv": ["| **Warstwa** | Capability pack |", "| **Scheme** | `kv://` / `log://` |", "| **Zależność** | `uricore>=0.1.8` |"],
    "urirdp": ["| **Warstwa** | Capability pack |", "| **Scheme** | `rdp://` |", "| **Zależność** | `uricore>=0.1.8` |", "| **Edge** | urirdpedge |", "| **Port** | 8795 |"],
    # edge CLIs
    "urirdpedge": ["| **Warstwa** | Edge CLI |", "| **CLI** | `urisys-rdp` |", "| **Runtime** | `uri_control.edge` (`uricore`) |", "| **Packi** | urirdp, urikvm, urihim, urishell, uribrowser, … |", "| **Port** | 8795 |"],
    "urikvmedge": ["| **Warstwa** | Edge CLI |", "| **CLI** | `urisys-kvm` |", "| **Runtime** | `uri_control.edge` (`uricore`) |", "| **Packi** | urikvm, urihim, uriocr, urillm |", "| **Port** | 8794 |"],
    "uristepperedge": ["| **Warstwa** | Edge CLI |", "| **Runtime** | `uri_control.edge` (`uricore`) |", "| **Pack** | uristepper |", "| **Port** | 8791 |"],
    # docker glue (in urisys tree or sibling)
    "urikvm-docker": ["| **Warstwa** | Docker glue |", "| **Obraz** | kvm/him/ocr/llm bundle |", "| **Build** | `docker build -f urikvm-docker/Dockerfile tellmesh/` |", "| **Zależności** | urirouter, uricore, urikvmedge |"],
    "urirdp-docker": ["| **Warstwa** | Docker glue |", "| **Obraz** | RDP desktop automation |", "| **Zależności** | urirouter, uricore, urirdpedge |"],
    "uribrowser-docker": ["| **Warstwa** | Docker glue |", "| **Scheme** | `browser://` |", "| **Zależności** | urirouter, uricore |"],
    "urienv-docker": ["| **Warstwa** | Docker glue |", "| **Scheme** | `env://` |", "| **Zależność** | uricore (`uri_control`) |"],
    "uristepper-docker": ["| **Warstwa** | Docker glue |", "| **Scheme** | `stepper://` |", "| **Zależności** | urirouter, uricore, uristepperedge |"],
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
        "Runtime edge: **`uri_control.edge`** w pakiecie **`uricore`** (legacy `urisysedge` usunięty 2026-06).",
        "Router intencji: **`urirouter`** (`uri_router`) — resolve + HTTP/MQTT delegate.",
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
        ("urisysedge.Runtime", "`uri_control.edge.Runtime`"),
        ("urisysedge", "`uricore` (`uri_control.edge`)"),
        ("`uricore` (`uri_control.edge`)>=0.1.0", "`uricore>=0.1.8`"),
        ("packages/python/urisysedge", "uricore/core/python/uri_control/edge"),
        ("tellmesh/urisysedge", "tellmesh/uricore"),
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
