# Dokumentacja urisys

Indeks dokumentacji monorepo **tellmesh/urisys** (stan: 2026-06-17).

## Start

| Dokument | Dla kogo | Opis |
|----------|----------|------|
| [`../README.md`](../README.md) | wszyscy | Instalacja, szybki start CLI |
| [`NODE-SETUP.md`](NODE-SETUP.md) | slave / lenovo | `urisys init`, node serve, lazy install, systemd |
| [`CLI.md`](CLI.md) | dev | `urisys call`, `flow`, `markpact`, `node serve` |
| [`EXAMPLES.md`](EXAMPLES.md) | dev | Przykłady URI i flow |

## Architektura i paczki

| Dokument | Opis |
|----------|------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Warstwy: CLI → edge Docker → flows; porty obrazów |
| [`PACKAGES.md`](PACKAGES.md) | Layout monorepo, `urisysedge`, duplikaty, `urioperators` |
| [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md) | Nowe schematy URI, hot-load, forward, `release_forwards` |
| [`FLOWS.md`](FLOWS.md) | Format `*.uri.flow.yaml`, uri2flow / uri3 |

## Dystrybucja i kontrakty

| Dokument | Opis |
|----------|------|
| [`DISTRIBUTION.md`](DISTRIBUTION.md) | PyPI · Markpact · GitHub OCI — trzy ścieżki packów |
| [`MARKPACT.md`](MARKPACT.md) | Format `*.markpact.md`, validate / compile / test |

## Automatyzacja biurowa

| Dokument | Opis |
|----------|------|
| [`OFFICE-AUTOMATION.md`](OFFICE-AUTOMATION.md) | Pipeline capture→OCR/LLM→akcja; office/mail/browser roadmap |

## Migracje (historyczne)

Kroki deduplikacji runtime — **zakończone**; zostawione jako referencja:

| Dokument | Temat |
|----------|-------|
| [`MIGRATION-STEP1.md`](MIGRATION-STEP1.md) | `urisysedge` wyodrębniony z `urirdpedge` |
| [`MIGRATION-STEP2.md`](MIGRATION-STEP2.md) | Shimy edge w obrazach Docker |
| [`MIGRATION-STEP3.md`](MIGRATION-STEP3.md) | `JsonlEventStore` / `Runtime` → `urisysedge` |

## Dokumentacja per obraz Docker

| Katalog | Schematy | Port |
|---------|----------|------|
| [`../urisys-node/`](../urisys-node/) | `node://`, `screen://`, lazy kvm/him/ocr/llm | **8790** |
| [`../urikvm-docker/`](../urikvm-docker/) | kvm, him, ocr, llm (+ office packi vendored) | **8794** |
| [`../urirdp-docker/`](../urirdp-docker/) | rdp, kvm, him, ocr, llm, shell, browser, env | **8795** / 3389 |
| [`../uribrowser-docker/`](../uribrowser-docker/) | browser | 8797 |
| [`../urienv-docker/`](../urienv-docker/) | env | 8798 |
| [`../uristepper-docker/`](../uristepper-docker/) | stepper | 8799 |
| [`../urisys-automation-lab/`](../urisys-automation-lab/) | stt, chat (deprecated), webrtc | 8099 |

## Analiza kodu (generowana)

| Plik | Opis |
|------|------|
| [`../project/map.toon.yaml`](../project/map.toon.yaml) | Mapa modułów, CC, alerty |
| [`../project/PACKAGES.md`](../project/PACKAGES.md) | Duplikaty z perspektywy code2llm |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Historia zmian |

## Stan projektu (skrót)

```text
urisys 0.1.33          CLI + init + doctor (uricore z GitHub wheel, nie PyPI)
urisys-node            64 passed / 6 skipped (unit)
kvm-release            tag urikvm-v0.1.5 — OCI ghcr + 8 release assets
hot-load               POST /uri/pack {pack} | {contract,version,catalog}
urioperators 0.1.0     wspólne helpery LLM (urillm ↔ urirdp_llm)
markpact-contracts     11/11 validate; portal publish wymaga MARKPACT_TOKEN
```

## Co dalej (otwarte)

1. Portal publish kontraktów kvm → markpact.com (`MARKPACT_TOKEN`)
2. PyPI: `urihim`, `uriocr`, `urillm`, `urioperators` (wheels build OK; upload wymaga `PYPI_TOKEN`)
3. Tor R faza 2: dedup OCR/HIM do `urioperators`
4. Reusable CI workflow dla `uribrowser` / `urirdp` bundle
5. Wayland E2E ydotool na lenovo

Szczegóły priorytetów: [`DISTRIBUTION.md`](DISTRIBUTION.md) · [`OFFICE-AUTOMATION.md`](OFFICE-AUTOMATION.md).
