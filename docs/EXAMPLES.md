# Przykłady w urisys

Katalog `examples/` jest płaski: każdy przykład ma własny katalog
`NN-nazwa/` oraz standardowe wejście `run.sh`.

| Przykład | Uruchomienie | Co demonstruje |
|----------|--------------|----------------|
| `01-call-uri` | `bash examples/01-call-uri/run.sh` | Pojedyncze URI przez CLI |
| `02-server-curl` | `bash examples/02-server-curl/run.sh` | HTTP `POST /uri/call` do `urisys serve` |
| `03-threaded-uri-runtime` | `bash examples/03-threaded-uri-runtime/run.sh` | Równoległe URI call i równoległe procesy flow |
| `04-markpact-browser-call` | `bash examples/04-markpact-browser-call/run.sh` | Markpact jako runtime manifest bez instalowania packa |
| `05-markpact-showcase-run-flow` | `bash examples/05-markpact-showcase-run-flow/run.sh` | Embedded flows z Markpact showcase |
| `06-frontend` | `bash examples/06-frontend/run.sh` | Minimalny frontend `uricontrol-js` |
| `07-mqtt-firmware-backend-frontend` | `bash examples/07-mqtt-firmware-backend-frontend/run.sh` | Firmware + backend + frontend przez MQTT |

## 01-call-uri

Wywołania przez centralny CLI z paczkami PyPI:

```bash
urisys --packs browser call "browser://default/page/open" \
  --payload '{"url":"https://example.com"}' \
  --approve

urisys --packs docker call "docker://container/web/command/restart" \
  --approve --dry-run
```

Wymaga: `uv sync`, zainstalowane paczki z `uri-packs`.

## 02-server-curl

HTTP bezpośrednio na `urisys serve`:

```bash
urisys --packs llm serve --port 8789
# w drugim terminalu:
bash examples/02-server-curl/run.sh
```

## 03-threaded-uri-runtime

Samowystarczalny smoke test równoległości: tworzy tymczasowy mock-pack, uruchamia
lokalny `urisys` HTTP runtime i sprawdza równoległe `/uri/call`, a potem odpala
kilka procesów CLI wykonujących ten sam flow.

```bash
bash examples/03-threaded-uri-runtime/run.sh
```

## 04-markpact-browser-call

```bash
source scripts/paths.sh
urisys --packs none \
  --markpact "$(markpact_contracts_packs)/uribrowser.markpact.md" \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve --dry-run
```

Markpact kompiluje się do manifestu w locie (`MarkpactManager`).

## 05-markpact-showcase-run-flow

```bash
bash examples/05-markpact-showcase-run-flow/run.sh
```

Skrypt wykonuje `markpact analyze`, `markpact run-flow` i `markpact run --as flow`
dla embedded flows z `uribrowser.showcase.markpact.md`.

## 06-frontend

`index.html` + `app.js` — klient HTTP do URI runtime (importy wskazują na sibling
repos `uri-packs`, `uricontrol-js`).

Uruchomienie:

```bash
bash examples/06-frontend/run.sh
```

Przycisk HTTP wymaga działającego backendu URI na `127.0.0.1:8789`.

## 07-mqtt-firmware-backend-frontend

Samowystarczalny przykład MQTT na trzech poziomach:

- firmware simulator publikuje `state`, `telemetry`, `event` i subskrybuje komendy,
- backend subskrybuje MQTT i wystawia HTTP API dla strony,
- frontend w JS woła endpointy `/api/device/...`, które publikują komendy MQTT.

```bash
bash examples/07-mqtt-firmware-backend-frontend/run.sh
```

Domyślna strona: `http://127.0.0.1:8097/`. Tryb CI/smoke:

```bash
bash examples/07-mqtt-firmware-backend-frontend/run.sh --smoke
```

## Flow w repo

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

## Ścieżka nauki

1. `examples/01-call-uri/run.sh` — pojedyncze URI przez CLI
2. `flows/device-maintenance.uri.flow.yaml` — sekwencja flow
3. `examples/03-threaded-uri-runtime/run.sh` — równoległe URI call i flow
4. `examples/07-mqtt-firmware-backend-frontend/run.sh` — firmware/backend/frontend MQTT
5. `urisys-automation-lab/scripts/docker-up.sh` + `docker-smoke.sh` — Docker stack
6. `python3 scripts/run_test_sessions.py --sessions lab-10-flows` — pełny E2E
7. `local-lab/scripts/run-all.sh` — markpact.com release chain

Więcej: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md), [`docs/FLOWS.md`](FLOWS.md).
