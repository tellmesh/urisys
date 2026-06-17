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
| `07-playwright-linkedin.uri.flow.yaml` | Playwright + Chrome profile via out-of-process browser worker |
| `08-kvm-linkedin.uri.flow.yaml` | **KVM-URI** — screen + kvm click-text + him keyboard + img2nl (no Playwright) |

**Flow 08** is the human-like path: native browser (`system-open`), eyes (`screen://`, `kvm://` screenshot, optional `img2nl://`), hands (`him://`). Playwright (flow 07) remains a fallback for DOM-heavy pages.

**Flow 07** no longer restarts the node. The `_upgrade-playwright` pre-flow pip-installs playwright/uribrowser and spawns the `browser` pack as an out-of-process **worker** (`node://lenovo/command/spawn-worker`); the router forwards `browser://` to it. Flow 07 likewise spawns a `kv` worker. Workers can be inspected/restarted/stopped independently:

```bash
python3 -m urisysnode.remote call "node://lenovo/query/workers"
python3 -m urisysnode.remote call "node://lenovo/command/restart-worker" --payload '{"name":"browser"}'
```

If a worker dies, the router's supervisor respawns it; no node restart is needed.

## Deploy router upgrade (urisys-node >= 0.1.8)

`urisys node serve` now **takes over its port**: it kills the previous instance
(pidfile first, then any process holding the port), waits for the port to free,
then binds. Re-running serve is an atomic restart — no external `pkill`. On exit
it also stops its child workers.

```bash
# from dev host, with wheel server up:
python3 -m urisysnode.remote pip-install http://192.168.188.212:8765/urisys_node-0.1.8-py3-none-any.whl
python3 -m urisysnode.remote restart        # detached `urisys node serve` takes over the port
python3 -m urisysnode.remote wait --timeout 60
python3 -m urisysnode.remote spawn-worker browser --force
python3 -m urisysnode.remote workers
```

## Single step

```bash
cd ../urisys-node
python3 -m urisysnode.remote call "kv://lenovo/runtime/query/discover"
```

Manifest: `session.manifest.yaml`
