# urisys-node

**Jawnie zainstalowany slave runtime** — nie zastępuje RDP/SSH, tylko dodaje warstwę URI z parowaniem, policy i audytem.

## Docker GUI (host → slave)

Test integracyjny: kontener z Xvfb + `urisys-node serve :8790`, host steruje przez HTTP/route-map.

```bash
bash scripts/run-urisys-node-docker-e2e.sh
```

Sesja z raportem (integracja z `run_test_sessions.py`):

```bash
bash scripts/run-urisys-node-docker-session.sh --run-id my-node-session
```

Nightly (lab-10 + node-docker, wymaga tellmesh + Docker):

```bash
bash scripts/run-lab-nightly.sh
# tylko node-docker:
URISYS_NIGHTLY_SESSIONS=urisys-node-docker-gui bash scripts/run-lab-nightly.sh
```

Szczegóły: [docker/README.md](docker/README.md)

## Instalacja

```bash
pip install urisys-node
```

Opcjonalnie: `pip install "urisys-node[real]"` (capture/OCR), `"urisys-node[discovery]"` (mDNS).

### Capability packs (kvm/him/ocr/llm)

| Pack | PyPI (po publikacji) | Dziś — monorepo |
|------|----------------------|-----------------|
| `urisys`, `urisys-node` | `pip install urisys-node` | ✅ |
| `uriscreen` | bundled w node | ✅ z `[real]` |
| `urikvm`, `urihim`, `uriocr`, `urillm` | osobne pakiety (pyproject gotowy) | **tylko ze źródła** |

**Nie używaj** `pip install urikvm` dopóki pakiety nie trafią na PyPI — stary meta-package `urikvm-docker-example` nie jest publikowany.

Zrzut ekranu (lenovo, od ręki):

```bash
pip install "urisys-node[real]"
URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen urisys-node serve --port 8790
```

KVM + HIM (mysz/klawiatura) — checkout monorepo:

```bash
bash scripts/install-kvm-packs-editable.sh
# albo ręcznie:
pip install -e packages/python/urisysedge
pip install -e 'urikvm-docker/packages/python/urikvm[real]' \
  -e 'urikvm-docker/packages/python/urihim[real]' \
  -e 'urikvm-docker/packages/python/uriocr[real]' \
  -e 'urikvm-docker/packages/python/urillm[vision]'
URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen,kvm,him urisys-node serve --port 8790
```

Hot-load po starcie (gdy `URISYS_NODE_ALLOW_PACK_LOAD=1`):

```bash
curl -X POST http://127.0.0.1:8790/uri/pack -H 'Content-Type: application/json' -d '{"pack":"kvm"}'
```

Worker OCI (markpact + GitHub artefakt, bez PyPI): `register_forward_pack()` w `urisysnode/serve.py` — forward HTTP do workera.

## Model

```txt
master / controller
  ↓  route map
transport: HTTP / WebSocket / WebRTC / relay
  ↓
slave: urisys-node (:8790)
  ↓
screen://  kvm://  him://  ocr://  llm://  …
```

Bez RDP/SSH i bez hardware KVM kontrola wymaga **lokalnej instalacji `urisys-node`** (za zgodą właściciela maszyny).

## Szybki start (dev)

```bash
cd urisys/urisys-node
pip install -e ".[real]"
export URISYS_NODE_SKIP_PAIRING=1   # tylko dev — w prod wymagaj enroll
urisys-node serve --port 8790
```

```bash
curl http://127.0.0.1:8790/health
curl http://127.0.0.1:8790/uri/routes

curl -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"screen://local/monitor/1/command/capture","payload":{"dry_run":true},"context":{"approved":true,"dry_run":true}}'
```

## Parowanie (Etap 1)

```bash
urisys-node enroll --controller https://master.local --code 482913
sudo systemctl enable --now urisys-node
```

## Master → slave

```bash
urisys-node call screen://slave-01/monitor/primary/query/frame \
  --route-map config/route-map.master.yaml \
  --nodes-registry config/nodes.registry.json \
  --dry-run --approve
```

Master tłumaczy `screen://slave-01/...` → `screen://local/...` na endpoincie slave.

## Endpointy slave

| Method | Path | Opis |
|--------|------|------|
| GET | `/health` | node_id, version, paired |
| GET | `/uri/routes` | lista tras URI |
| GET | `/events?limit=50` | audit JSONL |
| POST | `/uri/call` | wykonanie URI |

## Paczki w node

| Pack | Schemat |
|------|---------|
| `uriscreen` | `screen://` (mss, mock) |
| `urikvm` | `kvm://` (z urikvm-docker) |
| `urihim` | `him://` |
| `uriocr` | `ocr://` |
| `urillm` | `llm://` |
| `urisysnode` | `node://` identity/indicator |

## Roadmap

1. **LAN** — HTTP :8790, mDNS (`pip install -e ".[discovery]"`), Linux X11
2. **Relay** — outbound tunnel, brak otwartych portów
3. **Cross-platform** — Windows SendInput, macOS ScreenCaptureKit
4. **Hardware KVM** — `kvmhw://`
5. **Updates** — signed markpacts, `urisys update`

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/PAIRING.md](docs/PAIRING.md)
- [docs/SCREEN_BACKENDS.md](docs/SCREEN_BACKENDS.md)

## Powiązane

- [`urisys-automation-lab`](../urisys-automation-lab/) — demo UI + docker stack
- [`urirdp-docker`](../urirdp-docker/) — RDP container (inny use case — izolowany pulpit)
- [`urienv-docker`](../urienv-docker/) — `env://` secrets (może być pack w node)


## License

Licensed under Apache-2.0.
