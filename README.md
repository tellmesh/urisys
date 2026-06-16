# urisys

`urisys` jest centralnym runtime/controllerem dla URI control plane. Osobne paczki `uribrowser`, `uridocker`, `urisystemd` itd. (repo [`uri-packs`](../uri-packs)) dostarczają tylko `manifest.yaml` i handlery. Alternatywnie można używać jednoplikowych `UriPack Markpact`.

Nie używamy już `uripacks-serve` ani `uripacks call`. CLI to:

```bash
urisys --packs browser call browser://default/page/open --payload '{"url":"https://example.com"}' --approve
urisys --packs docker explain docker://container/web/query/status
urisys --packs browser,docker,systemd routes
urisys --packs all serve --port 8789
urisys --packs all flow flows/device-maintenance.uri.flow.yaml --approve --dry-run
```

## Managers/controllers

- `PackManager` ładuje paczki `uri*`, plain `manifest.yaml` i Markpact.
- `MarkpactManager` waliduje, kompiluje i testuje jednoplikowe `*.markpact.md`.
- `RuntimeManager` buduje `uri_control.UriControlRuntime` z registry, policy i event store.
- `UriController` wystawia `call`, `explain`, `routes`.
- `FlowController` uruchamia compact URI YAML flows.
- `ServerController` wystawia HTTP endpointy.
- `EventManager` czyta eventy JSONL.
- `BridgeManager` przekazuje URI envelopes do innych URI serverów.

## Markpact

Przykładowe pliki:

```text
markpacts/packs/uribrowser.markpact.md
markpacts/packs/urisystemd.markpact.md
markpacts/packs/uridom-js.markpact.md
```

Komendy:

```bash
urisys markpact validate markpacts/packs/uribrowser.markpact.md
urisys markpact compile markpacts/packs/uribrowser.markpact.md
urisys markpact routes markpacts/packs/uribrowser.markpact.md
urisys markpact test markpacts/packs/uribrowser.markpact.md
```

Wywołanie przez runtime bez instalowania paczki:

```bash
urisys --packs none \
  --markpact markpacts/packs/uribrowser.markpact.md \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve \
  --dry-run
```

## HTTP server

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

## Safe execution

Handlery są mock/safe domyślnie. `--approve` jest wymagane dla mutacji. `--allow-real` lub `URISYS_ALLOW_REAL=1` jest wymagane, zanim handler wykona realne komendy OS/urządzenia.

Więcej: `docs/MARKPACT.md` i `docs/CLI.md`.
