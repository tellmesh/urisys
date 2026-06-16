# `urisys` CLI

## Ładowanie zwykłych paczek

```bash
urisys --packs browser,docker routes
urisys --packs browser call browser://default/page/open --payload '{"url":"https://example.com"}' --approve
```

`--packs all` ładuje domyślne paczki: browser, desktop, android, docker, systemd, printer, camera, display, mail, llm, agent.

`--packs none` nie ładuje żadnej domyślnej paczki. To jest przydatne przy Markpact:

```bash
urisys --packs none --markpact markpacts/packs/uribrowser.markpact.md routes
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
