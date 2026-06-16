# urisys workspace

Workspace zawiera lekki, deterministyczny URI control plane:

```text
URI → manifest/Markpact → policy → handler → event → result
```

Nie ma tutaj ciężkiego hypervisora ani systemu agentowego. `urisys` jest centralnym runtime/controllerem, a osobne paczki `uri*` lub jednoplikowe `*.markpact.md` dostarczają capabilities i handlery.

## Skład

```text
uricore/        # niski poziom: parser, registry, dispatcher, event store, policy
uricore-js/     # JS/browser/Node runtime
urisys/         # kontrolery, managery, HTTP server, flow, Markpact
packages/python # osobne paczki: uribrowser, uridocker, urisystemd...
packages/js     # osobne paczki JS: uridom-js, uripage-js, urinode-js...
```

## Python URI packs

- `uribrowser` → `browser://`
- `uridesktop` → `desktop://`
- `uriandroid` → `android://`
- `uridocker` → `docker://`
- `urisystemd` → `systemd://`
- `uriprinter` → `printer://`
- `uricamera` → `camera://`
- `uridisplay` → `display://`
- `urimail` → `mail://`
- `urillm` → `llm://`
- `uriagent` → `agent://`

## JavaScript URI packs

- `uridom-js` → `dom://`
- `uripage-js` → `page://`
- `urinode-js` → `node://`
- `uribrowser-js` → browser-side umbrella package

## UriPack Markpact

Nowa wersja dodaje jednoplikowe paczki:

```text
urisys/markpacts/packs/uribrowser.markpact.md
urisys/markpacts/packs/urisystemd.markpact.md
urisys/markpacts/packs/uridom-js.markpact.md
```

Markpact jest źródłem paczki: zawiera manifest, kod handlerów, testy i dokumentację. `urisys` kompiluje go do cache runtime:

```text
*.markpact.md → .urisys/cache/markpacts/<pack>/<hash>/manifest.yaml + handlers
```

## Instalacja lokalna

```bash
python -m venv .venv
. .venv/bin/activate
./scripts/install-editable.sh
```

## Przykłady zwykłych paczek

Globalne opcje `--packs`, `--markpact`, `--events` podaje się przed subkomendą:

```bash
urisys --packs browser call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve
```

```bash
urisys --packs docker call docker://container/web/command/restart \
  --approve \
  --dry-run
```

```bash
urisys --packs all serve --port 8789
```

```bash
urisys --packs all flow urisys/flows/device-maintenance.uri.flow.yaml \
  --approve \
  --dry-run
```

## Przykłady Markpact

```bash
urisys markpact validate urisys/markpacts/packs/uribrowser.markpact.md
urisys markpact compile urisys/markpacts/packs/uribrowser.markpact.md
urisys markpact test urisys/markpacts/packs/uribrowser.markpact.md
```

Ładowanie bez instalowania paczki:

```bash
urisys --packs none \
  --markpact urisys/markpacts/packs/uribrowser.markpact.md \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve \
  --dry-run
```

## Architektura

```text
shell / frontend / backend / flow
  ↓
urisys controller
  ↓
urisys managers: PackManager, MarkpactManager, RuntimeManager, PolicyManager, EventManager
  ↓
uricore runtime
  ↓
separate uri* pack OR compiled Markpact manifest + handler
  ↓
event log / result
```

Dokumentacja:

- `urisys/docs/MARKPACT.md`
- `urisys/docs/CLI.md`
- `urisys/README.md`
