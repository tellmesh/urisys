# Lenovo remote flows

Reproducible URI flows for slave node `192.168.188.201:8790`.

## Run full session (Python)

```bash
cd urisys
python3 scripts/lenovo_remote_session.py --wait 90 --build-wheels --serve-wheels
```

Output: `output/test-sessions/lenovo-remote-*/` — `SESSION.md`, `responses/`, `screenshots/` (PNG extracted from base64), `flows/`, `meta.json`.

Extract images from an older session (responses had inline base64):

```bash
python3 scripts/lenovo_remote_session.py --extract-images output/test-sessions/lenovo-remote-YYYYMMDD-HHMMSS
```

## Flows (order)

| File | Purpose |
|------|---------|
| `01-health-probe.uri.flow.yaml` | HTTP + URI health, identity, packs |
| `02-install-packs.uri.flow.yaml` | hot-load kv, browser, office, mail |
| `03-system-introspect.uri.flow.yaml` | kv discover, log summarize, screen |
| `04-office-linkedin-dry.uri.flow.yaml` | office doc + publish dry-run + kv draft |
| `05-browser-linkedin-real.uri.flow.yaml` | system-open LinkedIn compose + screen + kv |
| `06-browser-auth-probe.uri.flow.yaml` | Chrome LinkedIn cookie probe + kv + screen |

## Single step

```bash
cd ../urisys-node
python3 -m urisysnode.remote call "kv://lenovo/runtime/query/discover"
```

Manifest: `session.manifest.yaml`
