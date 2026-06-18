# Przykłady w urisys

Katalog `examples/` oraz flow w podprojektach pokazują **trzy style** integracji z URI.

## `examples/shell/` — CLI urisys

### `call-uri.sh`

Wywołania przez centralny CLI z paczkami PyPI:

```bash
urisys call "browser://default/page/open" \
  --packs browser \
  --payload '{"url":"https://example.com"}' \
  --approve

urisys call "docker://container/web/command/restart" \
  --packs docker --approve --dry-run
```

Wymaga: `uv sync`, zainstalowane paczki z `uri-packs`.

### `server-curl.sh`

HTTP bezpośrednio na `urisys serve`:

```bash
urisys --packs all serve --port 8789
# w drugim terminalu — curl POST /uri/call
```

## `examples/markpact/` — Markpact bez instalacji paczki

### `browser-call.sh`

```bash
source scripts/paths.sh
urisys --packs none \
  --markpact "$(markpact_contracts_packs)/uribrowser.markpact.md" \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve --dry-run
```

Markpact kompiluje się do manifestu w locie (`MarkpactManager`).

## `examples/frontend/` — JavaScript (uricontrol-js)

`app.js` — klient HTTP do URI runtime (importy wskazują na sibling repos `uri-packs`, `uricontrol-js`).

Uruchomienie wymaga lokalnego serwera statycznego i działającego backendu URI.

## `flows/device-maintenance.uri.flow.yaml` — multi-pack flow

Mock flow przez systemd, docker, printer, display:

```bash
urisys --packs all flow flows/device-maintenance.uri.flow.yaml --approve --dry-run
```

`defaults.environment: mock` + `dry_run: true` — bezpieczna symulacja.

## Przykłady Docker (per obraz)

| Obraz | Skrypt / flow | Co demonstruje |
|-------|---------------|----------------|
| `urirdp-docker` | `scripts/test-real-docker.sh` | POST /uri/call na :8795 |
| `urirdp-docker` | `flows/rdp-kvm-smoke.uri.flow.yaml` | RDP + KVM |
| `urikvm-docker` | `scripts/test-real.sh` | Pipeline OCR+LLM+KVM |
| `uribrowser-docker` | `flows/browser-demo.uri.flow.yaml` | browser:// |
| `urienv-docker` | `flows/startup-env-check.uri.flow.yaml` | env:// policy |
| `uristepper-docker` | `flows/move-test.uri.flow.yaml` | stepper:// |
| `urisys-automation-lab` | `flows/01..10` | Pełny lab E2E |
| `urisys-automation-lab` | `scripts/docker-smoke.sh` | STT + chat dry-run |
| `local-lab` | `scripts/04-smoke.sh` | Registry + node resolve |

## uricontrol examples

Mock pack examples ship with the `uricore` package:

```bash
pip install -e ../uricore
python ../uricontrol/examples/call_browser_mock.py
```

To referencja dla handlerów `python://module:func` w manifestach.

## tellmesh/examples (poza urisys)

Compact URI flows (nl2uri, branching):

- `tellmesh/examples/15_compact_uri_flow/weather.uri.flow.yaml`
- `tellmesh/examples/15_compact_uri_flow/branching.uri.flow.yaml`

Expand:

```bash
uri2flow expand tellmesh/examples/15_compact_uri_flow/weather.uri.flow.yaml
```

## Ścieżka nauki (recommended)

1. `examples/shell/call-uri.sh` — pojedyncze URI przez CLI  
2. `flows/device-maintenance.uri.flow.yaml` — sekwencja flow  
3. `urisys-automation-lab/scripts/docker-up.sh` + `docker-smoke.sh` — Docker stack  
4. `python3 scripts/run_test_sessions.py --sessions lab-10-flows` — pełny E2E  
5. `local-lab/scripts/run-all.sh` — markpact.com release chain  

Więcej: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md), [`docs/FLOWS.md`](FLOWS.md).
