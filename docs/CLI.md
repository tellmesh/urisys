# `urisys` CLI

## Ładowanie zwykłych paczek

```bash
urisys --packs browser,docker routes
urisys --packs browser call browser://default/page/open --payload '{"url":"https://example.com"}' --approve
```

`--packs all` ładuje domyślne paczki: browser, desktop, android, docker, systemd, printer, camera, display, mail, llm, agent.

`--packs none` nie ładuje żadnej domyślnej paczki. To jest przydatne przy Markpact:

```bash
source scripts/paths.sh
urisys --packs none --markpact "$(markpact_contracts_packs)/uribrowser.markpact.md" routes
```

## Markpact

```bash
urisys markpact validate PATH.markpact.md
urisys markpact compile PATH.markpact.md
urisys markpact routes PATH.markpact.md
urisys markpact test PATH.markpact.md
```

## Server

```bash
urisys --packs all serve --host 127.0.0.1 --port 8789
```

Endpointy:

```text
GET  /health
GET  /uri/routes
GET  /uri/events
POST /uri/call
POST /uri/explain
```

## Node (slave)

Minimalna instalacja na maszynie zdalnej (lenovo):

```bash
pip install urisys
urisys node serve --host 0.0.0.0 --port 8790
```

Packi **kvm/him/ocr/llm** i backendy **`[real]`** doinstalowują się przy pierwszym URI (domyślnie `URISYS_NODE_AUTO_INSTALL=1`). Wyłączenie:

```bash
urisys node serve --no-auto-install
```

Szczegóły: [`NODE-SETUP.md`](NODE-SETUP.md) · [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md) · [`DISTRIBUTION.md`](DISTRIBUTION.md).

## Flow

```bash
urisys --packs all flow flows/device-maintenance.uri.flow.yaml --approve --dry-run
```

Format:

```yaml
flow:
  id: demo

defaults:
  approved: true
  dry_run: true
  environment: real

do:
  - systemd://unit/docker.service/query/status
  - docker://container/web/command/restart:
      reason: demo
```
