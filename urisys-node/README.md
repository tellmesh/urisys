# urisys-node

**Jawnie zainstalowany slave runtime** — nie zastępuje RDP/SSH, tylko dodaje warstwę URI z parowaniem, policy i audytem.

## Docker GUI (host → slave)

Test integracyjny: kontener z Xvfb + `urisys-node serve :8790`, host steruje przez HTTP/route-map.

```bash
bash scripts/run-urisys-node-docker-e2e.sh
```

Szczegóły: [docker/README.md](docker/README.md)

## Instalacja

```bash
pip install urisys-node
```

Opcjonalnie: `pip install "urisys-node[real]"` (capture/OCR), `"urisys-node[discovery]"` (mDNS).

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
