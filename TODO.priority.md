# urisys — TODO (priorytety)

> Pełna lista prefact: [`TODO.md`](TODO.md) · status org: [`../TODO_STATUS.md`](../TODO_STATUS.md)

## Zakończone (2026-06-17)

- [x] Migracja packów → `tellmesh/{repo}/` (32 packi, `pack_sync promote`)
- [x] Usunięcie vendored `packages/python/*` z urisys
- [x] PyPI `urisys` bez direct URL deps (`validate-pypi-metadata.sh`)
- [x] `urisys init` bez `git+https` (wheel urisys-node, bez hasła GitHub)
- [x] Wheel PEP 427: `urisys_node-*.whl` + fallback PyPI w `init`
- [x] GitHub [tellmesh/urisys-node](https://github.com/tellmesh/urisys-node) + Release v0.1.3
- [x] `deploy-lenovo-node.sh` — dynamic versions, sibling wheels
- [x] `bootstrap-lenovo-local.sh` — bootstrap na konsoli lenovo
- [x] Dokumentacja: `docs/REPOS.md`, `PACKAGES.md`, `DISTRIBUTION.md`, `NODE-SETUP.md`

## Otwarte (priorytet)

- [ ] **Lenovo online** — włączyć SSH + `urisys node serve` (ping OK, porty 22/8790 zamknięte)
- [ ] PyPI upload: `urihim`, `uriocr`, `urillm`, `urioperators`, `urimail`, `urioffice`, `urivql`, `urisys-node`
- [ ] `git init` + push bundle repos: `urirdp`, `urioperators`, `urikvmedge`, …
- [ ] Portal publish kontraktów kvm (`MARKPACT_TOKEN`)
- [ ] Tor R faza 2: OCR/HIM helpers → `urioperators`
- [ ] E2E lenovo: `bash scripts/run-office-simulate-lenovo.sh`

## Mapowanie repo

Zob. [`docs/REPOS.md`](docs/REPOS.md) — paczki URI są pod **tellmesh**, nie **semcod**.
