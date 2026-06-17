# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `docs/REPOS.md` — mapowanie paczek tellmesh → GitHub (tellmesh vs [semcod](https://github.com/semcod)); brak duplikatów vendored
- `src/urisys/node_install.py` — instalacja `urisys-node` z GitHub Release wheel (bez `git+https`, bez promptu hasła)
- `scripts/validate-pypi-metadata.sh` — guard przed direct URL w metadanych PyPI
- `scripts/ci-checkout-siblings.sh` — CI clone sibling repos obok urisys

### Changed
- Migracja 32 packów z `urisys/**/packages/python/*` → `tellmesh/{repo}/` (canonical source)
- `urisys init` — uricore + urisys-node tylko jako publiczne wheels; core pip bez git credentials
- Skrypty lenovo/deploy i `publish-pypi-packs.sh` — ścieżki sibling zamiast vendored
- Dokumentacja: `PACKAGES.md`, `DISTRIBUTION.md`, `NODE-SETUP.md`, `docs/README.md`

### Fixed
- `urisys init` — wheel URL `urisys_node-*.whl` (PEP 427); pip odrzucał `urisys-node-*.whl`
- `urisys init` — fallback PyPI `urisys-node` gdy brak GitHub Release; retry `urisysedge` po pip
- `urisys doctor` — `NameError: node_pip_spec` przy sprawdzaniu importu urisysnode
- PyPI upload HTTP 400 — usunięty `uricore @ https://…` z runtime deps wheela
- Przywrócone brakujące pliki po promote: `urienv/handlers.py`, `uriscreen/portal_capture.py`, `urirdp_kvm/display.py`

## [0.1.45] - 2026-06-17

### Docs
- Update README.md

### Test
- Update tests/test_edge_install.py

### Other
- Update uv.lock

## [0.1.44] - 2026-06-17

### Docs
- Update README.md
- Update TODO.priority.md
- Update docs/NODE-SETUP.md
- Update docs/REPOS.md

### Other
- Update scripts/bootstrap-lenovo-local.sh
- Update scripts/deploy-lenovo-node.sh
- Update scripts/lenovo-node-session.sh
- Update uv.lock

## [0.1.43] - 2026-06-17

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.1.42] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/NODE-SETUP.md
- Update docs/REPOS.md

### Test
- Update tests/test_node_install.py

### Other
- Update app.doql.less
- Update project/logic.pl
- Update project/map.toon.yaml
- Update scripts/publish-urisys-node-release.sh
- Update uv.lock

## [0.1.41] - 2026-06-17

### Docs
- Update README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- Update project/flow.png
- Update project/index.html
- ... and 5 more files

## [0.1.40] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update TODO.priority.md
- Update docs/NODE-SETUP.md
- Update docs/README.md
- Update docs/REPOS.md
- Update project/README.md
- ... and 1 more files

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 8 more files

## [0.1.10] - 2026-06-17

### Fixed
- Fix magic-numbers issues (ticket-58d889e9)
- Fix magic-numbers issues (ticket-f81ec0b9)
- Fix smart-return-type issues (ticket-03573fd4)
- Fix unused-imports issues (ticket-a13f62f5)
- Fix magic-numbers issues (ticket-c1c93d8b)
- Fix magic-numbers issues (ticket-da95d0ef)
- Fix duplicate-imports issues (ticket-7d2bd2f4)
- Fix unused-imports issues (ticket-f780fae2)
- Fix magic-numbers issues (ticket-164db83c)
- Fix ai-boilerplate issues (ticket-f5b58ecc)
- Fix unused-imports issues (ticket-9d0c6bee)
- Fix string-concat issues (ticket-792d4614)
- Fix unused-imports issues (ticket-bfa7a120)
- Fix ai-boilerplate issues (ticket-ade9f7fd)
- Fix unused-imports issues (ticket-7940e721)
- Fix relative-imports issues (ticket-980c1127)
- Fix string-concat issues (ticket-d4c2297e)
- Fix unused-imports issues (ticket-eb5997d0)
- Fix magic-numbers issues (ticket-1c49b283)
- Fix relative-imports issues (ticket-eef75004)
- Fix string-concat issues (ticket-11251076)
- Fix unused-imports issues (ticket-d5db6978)
- Fix magic-numbers issues (ticket-a358cac2)
- Fix unused-imports issues (ticket-3a630c1d)
- Fix relative-imports issues (ticket-0cb1c550)
- Fix smart-return-type issues (ticket-de570312)
- Fix unused-imports issues (ticket-915607a6)
- Fix relative-imports issues (ticket-abbaba0f)
- Fix string-concat issues (ticket-f3f0f7a9)
- Fix unused-imports issues (ticket-c6cc1e61)
- Fix relative-imports issues (ticket-ef645039)
- Fix unused-imports issues (ticket-fee16f7a)
- Fix magic-numbers issues (ticket-666babb8)
- Fix relative-imports issues (ticket-d7a55e27)
- Fix string-concat issues (ticket-a8453fb3)
- Fix unused-imports issues (ticket-d14be326)
- Fix relative-imports issues (ticket-392d98bf)
- Fix string-concat issues (ticket-b15ef75b)
- Fix unused-imports issues (ticket-c6054862)
- Fix magic-numbers issues (ticket-5f6752ac)
- Fix unused-imports issues (ticket-9610b8d9)
- Fix magic-numbers issues (ticket-64380a80)
- Fix relative-imports issues (ticket-eb858e59)
- Fix unused-imports issues (ticket-142f6917)
- Fix unused-imports issues (ticket-5562015f)
- Fix relative-imports issues (ticket-04abc7d9)
- Fix unused-imports issues (ticket-1d8883f8)
- Fix magic-numbers issues (ticket-e22cc686)
- Fix relative-imports issues (ticket-1fa4740c)

## [Unreleased] - 2026-06-17 — refactor & hardening

### Refactored (god-modules → focused units, behaviour byte-identical)
- `markpact_manager.py` (579→401L) — split out `markpact_models.py` (dataclasses + pure helpers) and `markpact_validation.py` (contract/bundle/implementation validators); extracted `_build_route` from `_compile_manifest` (CC 28→~6)
- `urillm.handlers._vision_analyze` (urikvm) — driver table `_VISION_DRIVERS` + `_analyze_openai`/`_analyze_litellm` (CC 22→~5); `_heuristic_analyze` split into `_find_target_box`/`_find_goal_box`/`_click_box` (CC 16→~7)
- `urirdp_llm.handlers.decide` — `_decide_litellm`/`_decide_openai`/`_decision_from_parsed` + dispatch (CC 23→~10)
- Each refactor verified by before/after output-snapshot diff (identical) + new characterization tests

### Added (capability hot-load primitives)
- `POST /uri/pack` + `load_pack_into_runtime()` — activate an installed pack into a live node (idempotent, secure-by-default behind `URISYS_NODE_ALLOW_PACK_LOAD=1`)
- `register_forward_pack()` + `urisysnode/forward.py` — route a contract's URI patterns to a resolved out-of-process worker (bridge to `ArtifactResolver` markpact.com→GitHub→worker)
- `hotload_release_pack()` + `POST /uri/pack {contract,version,catalog}` — full orchestration glue: pairing-gated and signature-gated, `fetch_release`→`verify_release`→`run_release`→`register_forward_pack` in one call; `/uri/pack` dispatches release vs. local-pack by request shape (403 when unpaired)
- `urisysnode/release_verify.py` — `verify_release()` signature gate (ed25519 over a canonical digest, keyid pinned via `URISYS_NODE_TRUSTED_KEYS`); **fail-closed** when `URISYS_NODE_REQUIRE_SIGNATURE=1` and the release is unsigned, signed by an untrusted key, or no crypto backend is present; pass-through (`verified: false`) until keys are provisioned
- `artifact_resolver.run_release(release, …)` — extracted from `resolve_from_release` so the glue runs the exact release it verified (no re-fetch)
- `artifact_resolver.parse_contract_spec()` / `contract_spec_from_release()` / `fetch_text()` — derive `{scheme, patterns}` straight from the UriContract referenced by a release; hot-load now wires the correct routes from the contract (source of truth) regardless of catalog response shape, falling back only when caller/release don't supply them
- Release-forward auto-provisioning at node boot — `forward_config.load_release_forward_entries()` / `wire_release_forward_packs()` + `build_runtime` wiring: a node reads `release_forwards: [{contract, version, catalog?, profile?}]` from config (or `URISYS_NODE_RELEASE_FORWARDS` env) and self-provisions each capability via `hotload_release_pack` at startup (best-effort: one failure does not abort the rest)
- READMEs for `urihim`/`uriocr`/`urillm` + `readme` in pyproject — wheels now `twine check` clean (PyPI pages non-empty)
- `.github/workflows/kvm-release.yml` — kvm bundle release pipeline (tag `urikvm-v*`): build the urikvm OCI image once, generate 4 per-contract `artifact-index.json` (port 8794, per-scheme capabilities) + commit once, then a matrix `register` job POSTs each release to markpact.com (no git race)
- 4 kvm contracts copied into `markpact-contracts/packs/` + `manifest.json` entries (`delivery: oci-forward`); `validate-all` → 11/11 PASS

### Fixed
- `artifact_resolver.run_release` — honors the selected artifact's `port`/`container_port` (urikvm worker listens on 8794, not the 8790 default) instead of hardcoding the container port
- `markpact_manager.load_pack_block` — removed duplicate (shadowing) definition
- `urisys-node/serve.py` — `urisys-node serve` no longer crashes when an optional pack (`urikvm`/`urihim`/…) is missing; best-effort load with a clear warning, hard error only for explicitly-named missing packs
- `PackManager` `--packs all` — skips uninstalled optional packs instead of `ModuleNotFoundError`; CLI runtime errors return clean JSON instead of tracebacks

### Tested / Verified
- Per-pack `pyproject.toml` (`urikvm`/`urihim`/`uriocr`/`urillm`) build + install + import standalone (`register` exported)
- Vendored `urisysedge` drift guard (AST-compare vs canonical), node pack hot-load + forward, vision/decide dispatch — new CI lanes `node-unit`, `pack-handlers-unit`
- `test_uriscreen_auto`/`test_ocr_llm` skip gracefully when Pillow/tesseract absent
- Host→Docker desktop and host→LAN node (`192.168.188.201:8790`) control verified live (capture + OCR)

## [0.1.39] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md

### Test
- Update tests/test_node_install.py

### Other
- Update app.doql.less
- Update planfile.yaml
- Update project/logic.pl
- Update project/map.toon.yaml
- Update uv.lock

## [0.1.38] - 2026-06-17

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- ... and 8 more files

## [0.1.37] - 2026-06-17

### Docs
- Update README.md

### Other
- Update scripts/deploy-lenovo-node.sh
- Update scripts/install-kvm-packs-editable.sh
- Update scripts/pack_registry.py
- Update scripts/publish-pypi-packs.sh
- Update scripts/run-office-simulate-lenovo.sh
- Update urisys-node/data/events.jsonl
- Update urisys-node/pyproject.toml
- Update uv.lock

## [0.1.36] - 2026-06-17

### Docs
- Update README.md
- Update docs/DISTRIBUTION.md
- Update docs/PACKAGES.md
- Update docs/README.md

### Test
- Update tests/test_kvm_pack_pyprojects.py
- Update tests/test_pypi_metadata.py
- Update tests/test_vendored_sync.py

### Other
- Update scripts/ci-checkout-siblings.sh
- Update scripts/ci-install-siblings.sh
- Update scripts/pack_registry.py
- Update scripts/pack_sync.py
- Update scripts/validate-pypi-metadata.sh
- Update uribrowser-docker/Dockerfile
- Update uribrowser-docker/packages/python/uribrowserdocker/__init__.py
- Update uribrowser-docker/packages/python/uribrowserdocker/handlers.py
- Update uribrowser-docker/packages/python/uribrowserdocker/routes.py
- Update uribrowser-docker/packages/python/uribrowseredge/__init__.py
- ... and 115 more files

## [0.1.35] - 2026-06-17

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update packages/python/urioperators/README.md
- Update packages/python/urisysedge/README.md
- Update urikvm-docker/packages/python/urihim/README.md
- Update urikvm-docker/packages/python/urillm/README.md
- Update urikvm-docker/packages/python/uriocr/README.md

### Test
- Update tests/test_kvm_pack_pyprojects.py
- Update tests/test_vendored_sync.py

### Other
- Update app.doql.less
- Update packages/python/urioperators/__init__.py
- Update packages/python/urioperators/llm_chat.py
- Update packages/python/urioperators/llm_decide.py
- Update packages/python/urioperators/llm_json.py
- Update packages/python/urioperators/llm_plan.py
- Update packages/python/urioperators/pyproject.toml
- Update packages/python/urioperators/tests/test_llm_helpers.py
- Update packages/python/urisysedge/__init__.py
- Update packages/python/urisysedge/env.py
- ... and 44 more files

## [0.1.34] - 2026-06-17

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/ARCHITECTURE.md
- Update docs/CLI.md
- Update docs/DISTRIBUTION.md
- Update docs/NODE-SETUP.md
- Update docs/OFFICE-AUTOMATION.md
- Update docs/PACK-EXTENSIBILITY.md
- ... and 5 more files

### Test
- Update tests/test_doctor_uricore.py
- Update tests/test_uricore_install.py

### Other
- Update VERSION
- Update app.doql.less
- Update packages/python/urioperators/__init__.py
- Update packages/python/urioperators/llm_chat.py
- Update packages/python/urioperators/llm_decide.py
- Update packages/python/urioperators/llm_json.py
- Update packages/python/urioperators/llm_plan.py
- Update packages/python/urioperators/pyproject.toml
- Update packages/python/urioperators/tests/test_llm_helpers.py
- Update project/analysis.toon.yaml
- ... and 32 more files

## [0.1.32] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMR.md
- Update docs/DISTRIBUTION.md
- Update docs/NODE-SETUP.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_init.py
- Update tests/test_kvm_pack_pyprojects.py

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 12 more files

## [0.1.31] - 2026-06-17

### Docs
- Update README.md
- Update SUMD.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_bootstrap.py
- Update tests/test_doctor.py
- Update tests/test_python_compat.py

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 13 more files

## [0.1.30] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/OFFICE-AUTOMATION.md
- Update urikvm-docker/packages/python/urihim/README.md
- Update urikvm-docker/packages/python/urillm/README.md
- Update urikvm-docker/packages/python/uriocr/README.md

### Other
- Update app.doql.less
- Update flows/browser-form-vql.uri.flow.yaml
- Update flows/email-mailpit.uri.flow.yaml
- Update flows/office-writer.uri.flow.yaml
- Update project/duplication.toon.yaml
- Update project/logic.pl
- Update project/map.toon.yaml
- Update scripts/run-email-mailpit-e2e.sh
- Update scripts/run-office-writer-e2e.sh
- Update scripts/run_test_sessions.py
- ... and 26 more files

## [0.1.29] - 2026-06-17

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- Update project/flow.png
- ... and 13 more files

## [0.1.28] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/NODE-SETUP.md
- Update docs/OFFICE-AUTOMATION.md

### Test
- Update tests/test_doctor.py

### Other
- Update scripts/deploy-lenovo-node.sh
- Update scripts/run-office-simulate-lenovo.sh
- Update scripts/run_test_sessions.py
- Update urisys-node/packages/python/urisysnode/artifact_resolver.py
- Update urisys-node/packages/python/urisysnode/cli.py
- Update urisys-node/packages/python/urisysnode/handlers.py
- Update urisys-node/packages/python/urisysnode/identity.py
- Update urisys-node/packages/python/urisysnode/release_verify.py
- Update urisys-node/packages/python/urisysnode/serve.py
- Update urisys-node/tests/test_release_hotload.py
- ... and 2 more files

## [0.1.27] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md

### Other
- Update app.doql.less
- Update project/logic.pl
- Update project/map.toon.yaml
- Update scripts/run-office-simulate-e2e.sh
- Update urikvm-docker/packages/python/urihim/handlers.py
- Update urikvm-docker/packages/python/urihim/pyproject.toml
- Update urikvm-docker/tests/test_him_driver.py
- Update urikvm-docker/tests/test_ocr_llm.py
- Update urisys-node/data/events.jsonl
- Update urisys-node/uv.lock
- ... and 1 more files

## [0.1.24] - 2026-06-17

### Added
- [`docs/PACK-EXTENSIBILITY.md`](docs/PACK-EXTENSIBILITY.md) — dodawanie packów (`imgl://`, forward worker), lifecycle po restarcie PC
- [`urisys-node/systemd/urisys-node-user.service`](urisys-node/systemd/urisys-node-user.service) — autostart node (systemd user, Wayland)
- Test regresji `test_pack_importable_uses_import_pack_module`
- [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md) — autostart, zmienne env, link do extensibility

### Changed
- `urihim.handlers._driver` — przy `allow_real` domyślnie `pyautogui` (X11); na Wayland auto `ydotool`
- `urihim` — driver `ydotool` dla mouse/keyboard (GNOME Wayland)
- [`README.md`](README.md) — pełna tabela docs, wersja 0.1.24
- [`docs/PACKAGES.md`](docs/PACKAGES.md), [`TODO.md`](TODO.md) — ekosystem imgl/vql, lenovo E2E

### Fixed
- `pack_resolver.import_pack_module` — orphaned code w `github_wheel_urls` łamało hot-load (`install-pack`, `/uri/pack`)
- Lazy load packów — nie downgrade'uje już zainstalowanej wersji przy pierwszym URI (`ensure_pack_for_uri`)

### Added (continued)
- `forward_config.py` — autostart forward packów z `URISYS_NODE_CONFIG.forwards` / env
- `node://…/command/register-forward` — hot-load workera (imgl/vql)
- `POST /uri/pack` + `install-pack` — parametr `force` do przeładowania packa po `pip install -U`
- `urisys-node/config/node-profile.lenovo.json` — profil Wayland + forward imgl/vql
- `urihim` 0.1.3 — driver `ydotool` (auto na Wayland)

### Published (GitHub Releases)
- `urihim` [v0.1.3](https://github.com/tellmesh/urihim/releases/tag/v0.1.3) — ydotool driver (Wayland)

### Fixed (2026-06-17, Docker E2E)
- `urirdp_shell` — przywrócony lokalny handler (shim `urishell` nie był w obrazie urirdp)

### Verified (Docker lab, host nvidia)
- `urisys-node-docker-gui` — `screen://` capture PASS
- `lab-10-flows` — 10 flow, 11/12 kroków (flow 04: expect screenshot)
- `urirdp-real-docker` — screenshot + OCR + click PASS

### Verified (lenovo 192.168.188.201)
- hot-load `him` bez restartu node po `shell://pip` + `install-pack`
- `screen://` capture via Wayland portal
- `shell://` bootstrap (Chrome, pip, skrypty)

## [0.1.19] - 2026-06-16

### Added
- [`docs/DISTRIBUTION.md`](docs/DISTRIBUTION.md) — trzy ścieżki dystrybucji packów (PyPI · Markpact · GitHub OCI), stan publikacji, równoległy podział pracy
- Osobne repo tellmesh: `urisysedge`, `urikvm`, `urihim`, `uriocr`, `urillm` (publikacja `goal -a`)
- `scripts/publish-pypi-packs.sh`, `tellmesh/scripts/publish-kvm-packs-goal.sh`
- `[kvm]` optional-deps + `uv.sources` dla vendored packów w root `pyproject.toml`
- `urisys-node`: `register_forward_pack()`, `load_pack_into_runtime()`, `POST /uri/pack`
- **`urisys node serve`** — slave HTTP node z lazy install packów (`URISYS_NODE_AUTO_INSTALL=1`)
- `urisysnode/pack_resolver.py` — PyPI mapowanie kvm/him/ocr/llm + `[real]` deps (mss, pyautogui, …)
- URI: `node://…/query/packs`, `node://…/command/install-pack`
- Testy: `urisys-node/tests/test_pack_auto_install.py`

### Changed
- Packi kvm vendored w monorepo — bez symlinków do sibling repo (fix walidacji `goal`)
- `urisysedge` bundlowany w wheel `urisys`; usunięty pusty stub `urisys-node/packages/python/urisysedge/`
- Domyślne `URISYS_NODE_PACKS=node,screen` — kvm/him/ocr/llm ładują się przy pierwszym URI
- [`docs/NODE-SETUP.md`](docs/NODE-SETUP.md) — główna ścieżka: `pip install urisys && urisys node serve`
- [`docs/PACKAGES.md`](docs/PACKAGES.md), [`README.md`](README.md), [`TODO.md`](TODO.md) — dystrybucja kvm
- Flow: `urisys-node/flows/bootstrap-kvm-pypi.uri.flow.yaml`, `remote-probe.uri.flow.yaml`

### Fixed
- Import `urisysedge` po reinstalacji editable urisys
- `goal -a` validation error: `Is a directory: packages/python/urisysedge`

### Published (PyPI)
- `urisysedge` 0.1.1, `urikvm` 0.1.1

## [0.1.10] - 2026-06-16

### Fixed
- Fix relative-imports issues (ticket-ec3c39ab)
- Fix unused-imports issues (ticket-81995907)
- Fix relative-imports issues (ticket-18a01fbd)

## [0.1.10] - 2026-06-16

### Fixed
- Fix smart-return-type issues (ticket-0ffc369f)
- Fix unused-imports issues (ticket-eaf7d426)
- Fix unused-imports issues (ticket-eff7ecf8)
- Fix smart-return-type issues (ticket-89864dc1)
- Fix smart-return-type issues (ticket-050b3e53)
- Fix magic-numbers issues (ticket-4a179497)
- Fix smart-return-type issues (ticket-b40ea12d)
- Fix relative-imports issues (ticket-94518524)
- Fix smart-return-type issues (ticket-7f39f9fb)
- Fix magic-numbers issues (ticket-52d52603)
- Fix ai-boilerplate issues (ticket-b4eb1a0e)
- Fix duplicate-imports issues (ticket-297f57b6)

## [0.1.10] - 2026-06-16

### Fixed
- Fix relative-imports issues (ticket-e3654290)
- Fix duplicate-imports issues (ticket-2eb137c9)
- Fix string-concat issues (ticket-230cdaab)
- Fix unused-imports issues (ticket-f9fba7fb)
- Fix magic-numbers issues (ticket-307efa54)
- Fix ai-boilerplate issues (ticket-8397b172)
- Fix unused-imports issues (ticket-f5106c26)
- Fix relative-imports issues (ticket-0957dc07)
- Fix smart-return-type issues (ticket-80341e57)
- Fix string-concat issues (ticket-d000a7c9)
- Fix unused-imports issues (ticket-fa870c45)
- Fix magic-numbers issues (ticket-4cc427d4)
- Fix string-concat issues (ticket-d0dbe11c)
- Fix unused-imports issues (ticket-db7f3e7b)
- Fix magic-numbers issues (ticket-ddf2b6d6)
- Fix ai-boilerplate issues (ticket-6f5dc895)
- Fix smart-return-type issues (ticket-d23cfa8b)
- Fix unused-imports issues (ticket-cae6d9a6)
- Fix ai-boilerplate issues (ticket-9f9aa9b5)
- Fix smart-return-type issues (ticket-1dc1eba6)

## [0.1.10] - 2026-06-16

### Fixed
- Fix smart-return-type issues (ticket-210b19c0)
- Fix relative-imports issues (ticket-9c936f2d)
- Fix smart-return-type issues (ticket-dbe59d30)
- Fix unused-imports issues (ticket-6e8eb7a8)
- Fix magic-numbers issues (ticket-c573dac2)

## [0.1.10] - 2026-06-16

### Fixed
- Fix unused-imports issues (ticket-30bb4018)
- Fix relative-imports issues (ticket-fc024f4e)
- Fix unused-imports issues (ticket-8f709667)
- Fix relative-imports issues (ticket-2c67b855)
- Fix unused-imports issues (ticket-518036f8)
- Fix magic-numbers issues (ticket-d841c7c8)
- Fix relative-imports issues (ticket-2793a7d8)
- Fix unused-imports issues (ticket-39409545)
- Fix magic-numbers issues (ticket-29f16a71)
- Fix ai-boilerplate issues (ticket-6553487a)
- Fix unused-imports issues (ticket-96f9891c)
- Fix relative-imports issues (ticket-e79d4ca3)
- Fix unused-imports issues (ticket-cec7f0cc)
- Fix smart-return-type issues (ticket-dcd4773e)
- Fix unused-imports issues (ticket-4bb42732)
- Fix relative-imports issues (ticket-c2e80424)
- Fix smart-return-type issues (ticket-fef6705c)
- Fix unused-imports issues (ticket-be76d941)
- Fix magic-numbers issues (ticket-5cc012a1)
- Fix unused-imports issues (ticket-b6345a65)
- Fix magic-numbers issues (ticket-85c65bbf)
- Fix unused-imports issues (ticket-b776131d)
- Fix relative-imports issues (ticket-d7dcad72)
- Fix unused-imports issues (ticket-9ce258ce)
- Fix relative-imports issues (ticket-cd8357c3)
- Fix unused-imports issues (ticket-a12701ce)
- Fix relative-imports issues (ticket-1c621c42)
- Fix string-concat issues (ticket-96b9c612)
- Fix unused-imports issues (ticket-705cadeb)
- Fix unused-imports issues (ticket-d6cd4406)
- Fix relative-imports issues (ticket-5db70ec6)
- Fix unused-imports issues (ticket-8a5b7a82)
- Fix unused-imports issues (ticket-1e40f542)
- Fix magic-numbers issues (ticket-567b3ea0)
- Fix smart-return-type issues (ticket-2cfefb7a)
- Fix unused-imports issues (ticket-1ae2965a)
- Fix smart-return-type issues (ticket-1375e09a)
- Fix unused-imports issues (ticket-dde03b11)
- Fix smart-return-type issues (ticket-44406fec)
- Fix unused-imports issues (ticket-63daebec)
- Fix string-concat issues (ticket-867db8ff)
- Fix unused-imports issues (ticket-10e09066)
- Fix relative-imports issues (ticket-a96c07b1)
- Fix smart-return-type issues (ticket-723fc429)
- Fix unused-imports issues (ticket-15a3ac4f)
- Fix magic-numbers issues (ticket-8b5e15f4)
- Fix ai-boilerplate issues (ticket-b7278838)
- Fix relative-imports issues (ticket-2f589957)
- Fix unused-imports issues (ticket-fd90cfb5)
- Fix unused-imports issues (ticket-cb4191e3)
- Fix relative-imports issues (ticket-fc232685)
- Fix smart-return-type issues (ticket-948f8f39)
- Fix unused-imports issues (ticket-48cf8a55)
- Fix relative-imports issues (ticket-a5314e38)
- Fix smart-return-type issues (ticket-0be3c18c)
- Fix unused-imports issues (ticket-d6a10364)
- Fix magic-numbers issues (ticket-ae38cbc6)
- Fix relative-imports issues (ticket-41936084)
- Fix relative-imports issues (ticket-2b301453)
- Fix unused-imports issues (ticket-8cd3f7ed)
- Fix ai-boilerplate issues (ticket-6b5fbb54)
- Fix relative-imports issues (ticket-c6c53d0b)
- Fix unused-imports issues (ticket-38627265)
- Fix relative-imports issues (ticket-931df1dc)
- Fix string-concat issues (ticket-b8bfa4e2)
- Fix unused-imports issues (ticket-4e66aedc)
- Fix relative-imports issues (ticket-f535cd8e)
- Fix unused-imports issues (ticket-04f7c97a)
- Fix relative-imports issues (ticket-511e94e4)
- Fix unused-imports issues (ticket-caff6088)
- Fix relative-imports issues (ticket-2e475f9b)
- Fix unused-imports issues (ticket-d6481792)
- Fix unused-imports issues (ticket-5e4dd8a5)
- Fix llm-generated-code issues (ticket-c1add2de)
- Fix relative-imports issues (ticket-467573e1)
- Fix string-concat issues (ticket-77ea7993)
- Fix unused-imports issues (ticket-81c1b4bc)
- Fix relative-imports issues (ticket-7bfd67bd)
- Fix unused-imports issues (ticket-11a0bc94)
- Fix magic-numbers issues (ticket-2ffd0049)
- Fix string-concat issues (ticket-f6ad4ab8)
- Fix unused-imports issues (ticket-e1c5ccda)
- Fix magic-numbers issues (ticket-b4aa982c)
- Fix relative-imports issues (ticket-1487c601)
- Fix smart-return-type issues (ticket-a0438550)
- Fix unused-imports issues (ticket-41fe5e45)
- Fix magic-numbers issues (ticket-b44b1074)
- Fix ai-boilerplate issues (ticket-eda2163a)
- Fix relative-imports issues (ticket-dc3036ef)
- Fix smart-return-type issues (ticket-3bbd4861)
- Fix string-concat issues (ticket-0fcc2acc)
- Fix unused-imports issues (ticket-7a036879)
- Fix magic-numbers issues (ticket-1538135c)
- Fix string-concat issues (ticket-b106be37)
- Fix unused-imports issues (ticket-c2e8d82c)

## [Unreleased]

## [0.1.26] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/DISTRIBUTION.md
- Update docs/OFFICE-AUTOMATION.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update flows/office-simulate-tick.uri.flow.yaml
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 30 more files

## [0.1.25] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/ARCHITECTURE.md
- Update docs/DISTRIBUTION.md
- Update docs/FLOWS.md
- Update docs/NODE-SETUP.md
- Update docs/PACK-EXTENSIBILITY.md
- Update docs/PACKAGES.md
- Update project/README.md
- ... and 2 more files

### Other
- Update VERSION
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 25 more files

## [0.1.23] - 2026-06-17

### Docs
- Update README.md

### Other
- Update urisys-node/packages/python/uriscreen/backends.py
- Update urisys-node/packages/python/uriscreen/handlers.py
- Update urisys-node/packages/python/uriscreen/portal_capture.py
- Update urisys-node/packages/python/urisysnode/display_bootstrap.py
- Update urisys-node/packages/python/urisysnode/serve.py
- Update urisys-node/tests/test_uriscreen_auto.py
- Update uv.lock

## [0.1.22] - 2026-06-16

### Docs
- Update README.md
- Update docs/NODE-SETUP.md

### Other
- Update urirdp-docker/packages/python/urirdp_shell/handlers.py
- Update urirdp-docker/packages/python/urirdp_shell/routes.py
- Update urisys-node/config/route-map.lenovo.yaml
- Update urisys-node/flows/bootstrap-kvm-github.uri.flow.yaml
- Update urisys-node/packages/python/urishell/__init__.py
- Update urisys-node/packages/python/urishell/handlers.py
- Update urisys-node/packages/python/urishell/routes.py
- Update urisys-node/packages/python/urisysnode/pack_resolver.py
- Update urisys-node/packages/python/urisysnode/serve.py
- Update urisys-node/tests/test_urishell.py
- ... and 1 more files

## [0.1.21] - 2026-06-16

### Docs
- Update README.md
- Update TODO.md
- Update docs/DISTRIBUTION.md
- Update docs/NODE-SETUP.md

### Other
- Update scripts/lenovo-node-session.sh
- Update urisys-node/config/nodes.registry.json
- Update urisys-node/config/route-map.lenovo.yaml
- Update urisys-node/packages/python/urisysnode/handlers.py
- Update urisys-node/packages/python/urisysnode/pack_resolver.py
- Update urisys-node/packages/python/urisysnode/serve.py
- Update urisys-node/tests/test_pack_github.py
- Update uv.lock

## [0.1.20] - 2026-06-16

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/CLI.md
- Update docs/DISTRIBUTION.md
- Update docs/FLOWS.md
- Update docs/MARKPACT.md
- Update docs/NODE-SETUP.md
- Update docs/PACKAGES.md
- Update urisys-node/README.md

### Other
- Update scripts/install-kvm-packs-editable.sh
- Update scripts/remote-node-smoke.sh
- Update urisys-node/flows/bootstrap-kvm-pypi.uri.flow.yaml
- Update urisys-node/flows/remote-probe.uri.flow.yaml
- Update urisys-node/packages/python/urisysnode/handlers.py
- Update urisys-node/packages/python/urisysnode/pack_resolver.py
- Update urisys-node/packages/python/urisysnode/routes.py
- Update urisys-node/packages/python/urisysnode/serve.py
- Update urisys-node/tests/test_pack_auto_install.py
- Update uv.lock

## [0.1.19] - 2026-06-16

### Docs
- Update README.md
- Update urisys-node/packages/python/urisysedge/README.md

### Other
- Update urisys-node/data/events.jsonl
- Update uv.lock

## [0.1.18] - 2026-06-16

### Docs
- Update README.md
- Update packages/python/urisysedge/README.md

### Test
- Update tests/test_kvm_pack_pyprojects.py

### Other
- Update packages/python/urisysedge
- Update packages/python/urisysedge/__init__.py
- Update packages/python/urisysedge/env.py
- Update packages/python/urisysedge/pyproject.toml
- Update packages/python/urisysedge/runtime.py
- Update scripts/install-kvm-packs-editable.sh
- Update urikvm-docker/packages/python/urihim
- Update urikvm-docker/packages/python/urihim/__init__.py
- Update urikvm-docker/packages/python/urihim/handlers.py
- Update urikvm-docker/packages/python/urihim/pyproject.toml
- ... and 20 more files

## [0.1.17] - 2026-06-16

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/MIGRATION-STEP3.md
- Update docs/PACKAGES.md
- Update project/README.md
- Update project/context.md
- Update urikvm-docker/README.md
- ... and 4 more files

### Test
- Update tests/test_kvm_pack_pyprojects.py
- Update tests/test_session_report_events.py

### Other
- Update app.doql.less
- Update packages/python/urisysedge
- Update packages/python/urisysedge/__init__.py
- Update packages/python/urisysedge/env.py
- Update packages/python/urisysedge/runtime.py
- Update planfile.yaml
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- ... and 72 more files

## [0.1.16] - 2026-06-16

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/FLOWS.md
- Update project/README.md
- Update project/context.md
- Update urisys-node/README.md
- Update urisys-node/docker/README.md

### Test
- Update tests/test_markpact.py

### Other
- Update app.doql.less
- Update planfile.yaml
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 36 more files

## [0.1.15] - 2026-06-16

### Docs
- Update README.md

### Other
- Update urisys-automation-lab/data/events.jsonl
- Update urisys-node/data/events.jsonl
- Update uv.lock

## [0.1.14] - 2026-06-16

### Docs
- Update README.md
- Update urisys-automation-lab/README.md
- Update urisys-automation-lab/docs/10_AUTOMATIONS.md
- Update urisys-automation-lab/markpacts/log-flow.contract.markpact.md

### Other
- Update scripts/run-nl-log-smoke.sh
- Update scripts/run-smoke-all.sh
- Update scripts/run_test_sessions.py
- Update scripts/session_report.py
- Update urirdp-docker/packages/python/urirdp/handlers.py
- Update urisys-automation-lab/Dockerfile
- Update urisys-automation-lab/data/events.jsonl
- Update urisys-automation-lab/flows/03_open_browser_gui.uri.flow.yaml
- Update urisys-automation-lab/flows/04_browser_download_file.uri.flow.yaml
- Update urisys-automation-lab/flows/05_fill_form_gui.uri.flow.yaml
- ... and 7 more files

## [0.1.13] - 2026-06-16

### Docs
- Update README.md
- Update urisys-automation-lab/markpacts/urillm-decide.contract.markpact.md

### Other
- Update urisys-automation-lab/tests/test_flow_08_plan.py
- Update urisys-automation-lab/tests/test_lab_handlers.py
- Update urisys-node/data/events.jsonl
- Update uv.lock

## [0.1.12] - 2026-06-16

### Docs
- Update README.md

### Other
- Update urisys-automation-lab/data/events.jsonl

## [0.1.11] - 2026-06-16

### Docs
- Update README.md
- Update docs/MIGRATION-STEP1.md
- Update docs/MIGRATION-STEP2.md
- Update docs/PACKAGES.md

### Other
- Update .dockerignore
- Update .gitignore
- Update local-lab/scripts/01-validate-markpact.sh
- Update local-lab/scripts/install-urisys.sh
- Update project.sh
- Update scripts/run-lab-e2e.sh
- Update urirdp-docker/Dockerfile
- Update urisys-automation-lab/Dockerfile
- Update urisys-automation-lab/data/events.jsonl
- Update uv.lock

## [0.1.10] - 2026-06-16

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.1.9] - 2026-06-16

### Docs
- Update README.md
- Update docs/FLOWS.md
- Update docs/MIGRATION-STEP2.md
- Update project/PACKAGES.md

### Other
- Update .gitignore
- Update local-lab/scripts/02-build-publish.sh
- Update scripts/paths.sh
- Update uribrowser-docker/Dockerfile
- Update uribrowser-docker/packages/python/uribrowseredge/runtime.py
- Update urikvm-docker/Dockerfile
- Update urikvm-docker/packages/python/urikvmedge/env.py
- Update urikvm-docker/packages/python/urikvmedge/runtime.py
- Update urisys-automation-lab/Dockerfile
- Update urisys-automation-lab/server/flow_runner.py
- ... and 1 more files

## [0.1.8] - 2026-06-16

### Docs
- Update README.md
- Update urisys-automation-lab/markpacts/urichat.contract.markpact.md
- Update urisys-automation-lab/markpacts/uristt.contract.markpact.md
- Update urisys-automation-lab/markpacts/uriwebrtc.contract.markpact.md
- Update urisys-node/markpacts/uriscreen.contract.markpact.md
- Update urisys-node/markpacts/urisys-node.contract.markpact.md

### Test
- Update tests/test_markpact.py

### Other
- Update data/events.jsonl
- Update scripts/run_test_sessions.py
- Update scripts/validate-all-markpacts.sh
- Update urirdp-docker/Dockerfile
- Update urirdp-docker/config/env-policy.yaml
- Update urirdp-docker/config/rdp-kvm-profile.json
- Update urirdp-docker/config/rdp-kvm-profile.real.json
- Update urirdp-docker/docker-compose.rdp-e2e.yml
- Update urirdp-docker/docker-compose.yml
- Update urirdp-docker/docker/entrypoint.sh
- ... and 27 more files

## [0.1.7] - 2026-06-16

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md

### Other
- Update app.doql.less
- Update project/logic.pl
- Update project/map.toon.yaml
- Update releases/uristepper-pack/0.1.0/artifact-index.json
- Update urisys-automation-lab/data/events.jsonl

## [0.1.6] - 2026-06-16

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md
- Update uristepper-docker/markpacts/uristepper.pack.markpact.md

### Other
- Update app.doql.less
- Update local-lab/builder/Dockerfile
- Update local-lab/docker-compose.yml
- Update local-lab/generated/.gitkeep
- Update local-lab/generated/artifact-index.json
- Update local-lab/node-profile.local.yaml
- Update local-lab/node/Dockerfile
- Update local-lab/scripts/00-init-nexus.sh
- Update local-lab/scripts/01-validate-markpact.sh
- Update local-lab/scripts/02-build-publish.sh
- ... and 25 more files

## [0.1.5] - 2026-06-16

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- ... and 19 more files

## [0.1.4] - 2026-06-16

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md
- Update uribrowser-docker/README.md
- Update uribrowser-docker/docs/PORTABILITY.md
- Update uribrowser-docker/markpacts/uribrowser-python.markpact.md
- ... and 37 more files

### Test
- Update testql-scenarios/generated-api-smoke.testql.toon.yaml
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml

### Other
- Update app.doql.less
- Update planfile.yaml
- Update prefact.yaml
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 167 more files

## [0.1.3] - 2026-06-16

### Docs
- Update README.md

### Other
- Update project.sh
- Update tree.sh

## [0.1.2] - 2026-06-16

### Docs
- Update README.md
- Update uristepper-docker/README.md
- Update uristepper-docker/docs/ESP32P4_NOTES.md
- Update uristepper-docker/docs/ROUTING.md
- Update uristepper-docker/markpacts/uristepper-docker.bundle.markpact.md
- Update uristepper-docker/markpacts/uristepper-python-mock.markpact.md
- Update uristepper-docker/markpacts/uristepper-rpi-gpio-python.markpact.md
- Update uristepper-docker/markpacts/uristepper.contract.markpact.md

### Other
- Update scripts/test-goal.sh
- Update uristepper-docker/.dockerignore
- Update uristepper-docker/.gitignore
- Update uristepper-docker/Dockerfile
- Update uristepper-docker/Makefile
- Update uristepper-docker/config/device-profile.json
- Update uristepper-docker/config/device-profile.rpi3.example.json
- Update uristepper-docker/docker-compose.rpi3.example.yml
- Update uristepper-docker/docker-compose.yml
- Update uristepper-docker/flows/move-test.uri.flow.yaml
- ... and 15 more files

## [0.1.1] - 2026-06-16

### Docs
- Update README.md
- Update docs/CLI.md
- Update docs/MARKPACT.md
- Update markpacts/packs/uribrowser.markpact.md
- Update markpacts/packs/uridocker.markpact.md
- Update markpacts/packs/uriprinter.markpact.md
- Update markpacts/packs/urisystemd.markpact.md
- Update markpacts/packs/uriusb.markpact.md
- Update urienv-docker/README.md
- Update urienv-docker/docs/ENV_URI.md
- ... and 6 more files

### Test
- Update tests/test_markpact.py
- Update tests/test_source_manager.py

### Other
- Update .gitignore
- Update schemas/uripack-markpact.schema.json
- Update scripts/test-goal.sh
- Update urienv-docker/Dockerfile
- Update urienv-docker/docker-compose.yml
- Update urienv-docker/docker/config/env-policy.yaml
- Update urienv-docker/docker/secrets/markpact_token.txt
- Update urienv-docker/docker/secrets/smtp_password.txt
- Update urienv-docker/flows/mutate-process-env.uri.flow.yaml
- Update urienv-docker/flows/startup-env-check.uri.flow.yaml
- ... and 53 more files

