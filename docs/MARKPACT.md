# UriPack Markpact

`UriPack Markpact` to jednoplikowy format paczki URI dla `urisys`. Służy do szybkiego tworzenia cienkich warstw nad usługą, urządzeniem, stroną WWW albo procesem bez budowania pełnej paczki Python/JS.

Najważniejsza zasada:

```text
Markpact procesu  = CO (sekwencja URI, policy, uses)
Runtime resolver  = GDZIE i JAK (targets, transport, adapter)
marksync          = sync źródeł + generowanie plików per środowisko
urisys            = compile, wykonanie, urisys://flow/, policy, eventy
```

Pełny opis trzech warstw: [`docs/PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md).

Nie należy traktować Markdowna procesu jako bezpośredniego formatu produkcyjnego na urządzeniu. `urisys` czyta bloki `markpact:*`, waliduje i materializuje do cache; marksync synchronizuje źródła i generuje artefakty resolvera / deploymentu.

## Minimalny plik

```markdown
# UriPack: demo

```yaml markpact:pack
apiVersion: urisys.io/v1
kind: UriPack
metadata:
  id: uridemo
  version: 0.1.0
  language: python
schemes: [demo]
capabilities:
  - id: demo.echo
    uri: demo://local/query/echo
    kind: query
    operation: echo
    handler: markpact://self/python/echo
    side_effects: false
    approval: not_required
```

```python markpact:handler id=echo
def handle(payload, context):
    return {"echo": payload}
```
```

W prawdziwym pliku nie zagnieżdżaj bloków ``` w środku innych bloków Markdown. Dla dokumentacji w `markpact:docs` używaj wciętych przykładów albo zwykłego tekstu.

## Obsługiwane bloki

| Blok | Rola |
|---|---|
| `yaml markpact:pack` | Manifest paczki: URI, capability, policy, runtime. Wymagany dokładnie jeden. |
| `python markpact:handler id=<id>` | Handler runtime Python. Musi definiować `handle(payload, context)`. |
| `yaml markpact:tests` | Testy wykonywane przez `urisys markpact test`. |
| `yaml markpact:flow id=<id>` | Use case / integracja — wyciągane do cache przy compile. |
| `proto markpact:proto path=<rel>` | Osadzone typy `.proto` (referencje `command_type`). |
| `markdown markpact:docs` | Dokumentacja użytkowa wyciągana do cache. |
| `js markpact:handler id=<id>` | Źródło JS dla przyszłego `urisys-js`; Python runtime go nie wykonuje. |

## Handler `urisys://flow/<flow-id>`

Proces może być opisany jako `markpact:flow`, a jednocześnie wystawiony jako zwykła capability URI — bez osobnej paczki Python/JS na każdy proces.

```yaml
capabilities:
  - uri: process://machine-cycle/command/run
    kind: command
    operation: run
    handler: urisys://flow/machine-cycle
```

To **nie** jest handler użytkownika. To wbudowany kontroler urisys: przy wywołaniu capability ładuje skompilowany `flows/<id>.uri.flow.yaml` i wykonuje kroki przez platformowy resolver URI (`runtime.call`).

Ścieżka w runtime:

```text
process://…/command/run  →  urisys://flow/<id>  →  kroki flow  →  resolver platformowy
```

Przy compile markpact zapisuje mapowanie w `manifest.yaml`:

```yaml
urisys:
  flows_dir: …/flows
  flows:
    machine-cycle: …/flows/machine_cycle.uri.flow.yaml
handlers:
  urisys:
    machine_cycle.run: urisys://flow/machine-cycle
```

### UriProcess (proces produkcyjny)

Przykład: [`machine-cycle-process.markpact.md`](../../markpact-contracts/packs/machine-cycle-process.markpact.md) (produkcja) i [`desktop-automation-processes.markpact.md`](../../markpact-contracts/packs/desktop-automation-processes.markpact.md) (automation example 39).

### URI Flow Contract

Proces = graf wywołań URI (`do:` sekwencja lub `{id, uri, after}`). Flow **nie** wskazuje handlerów ani transportu.

```bash
urisys markpact analyze markpact-contracts/packs/desktop-automation-processes.markpact.md
# → requires.schemes per flow (kvm, ocr, shell, …)
```

Reguły profilu: [`docs/PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md).

| Warstwa | Plik / narzędzie | Odpowiedzialność |
|---------|------------------|------------------|
| Proces | `*.markpact.md` (process) | **Co** — flow, capability `process://…`, `urisys://flow/` |
| Resolver | `generated/*/urisys.runtime.yaml` | **Gdzie/jak** — `targets`, transport, adapter ([przykład](../../markpact-contracts/packs/examples/urisys.runtime.resolver.yaml)) |
| Sync | [marksync](https://github.com/markpact/marksync) | CRDT sync Markpactów + generowanie artefaktów per env |

- **Etap 1** — `markpact:flow` opisuje proces (nie tylko smoke): `machine-cycle`, … ✅
- **Etap 2** — `urisys://flow/<id>` + `process://…/command/run` ✅
- **Etap 3** — resolver `targets:` poza procesem — loader + `resolve_uri` w `Runtime.call` ✅ → [`PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md)
- **Etap 4** — marksync → `generated/{linux,server,esp32}/` ✅ → `export-platform`, plugin `urisys`

Paczki URI (`uristepper`, `uriscreen`, …) bez zmian — proces to klej:

```text
URI packi = klocki  |  flow = proces  |  resolver = platforma  |  marksync = sync+generate  |  urisys = wykonanie
```

## Komendy

```bash
source scripts/paths.sh
PACK="$(markpact_contracts_packs)/uribrowser.markpact.md"

urisys markpact validate "$PACK"
urisys markpact compile "$PACK"
urisys markpact routes "$PACK"
urisys markpact test "$PACK"
urisys markpact analyze "$PACK"
urisys markpact materialize "$PACK"
urisys markpact materialize "$PACK" --platforms linux,server,esp32
urisys markpact export-platform markpact-contracts/packs/machine-cycle-process.markpact.md
urisys markpact run "$PACK" --as flow --approve --dry-run
urisys markpact run "$PACK#shell-smoke" --as flow --approve --dry-run   # jeden flow z fragmentu
urisys markpact run "$PACK" --as service --port 8789
```

### Tryby `markpact run --as`

| Tryb | Rola |
|------|------|
| `pack` | rejestracja manifestu → lista tras |
| `service` | HTTP `POST /uri/call` — proces `scheme://` |
| `flow` | osadzone flow (z auto-load zależności z `uses:`) |
| `interface` | katalog tras dla człowieka/CLI |
| `adapter` | JSON kontraktu integracji (routes + uses + wire) |

Domyślny tryb z bloku `markpact:run`; nadpisanie: `--as`.

### Resolver i export platform (UriProcess)

Proces **nie** zawiera `targets:` — resolver ładuje się osobno:

```bash
export URISYS_RESOLVER_CONFIG=markpact-contracts/packs/examples/urisys.runtime.resolver.yaml
# lub po materialize:
export URISYS_RESOLVER_CONFIG=.markpact/desktop_automation_processes/generated/linux/urisys.runtime.yaml

urisys markpact run markpact-contracts/packs/desktop-automation-processes.markpact.md \
  --as flow --approve --dry-run

bash scripts/marksync-materialize.sh markpact-contracts/packs/desktop-automation-processes.markpact.md
```

Szczegóły: [`docs/PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md).

Unpack: `.markpact/{id}/{hash}/` w cwd (`--out`).

Generator (thin, w paczce):

```bash
python3 scripts/generate_pack_markpacts.py
python3 scripts/generate_pack_markpacts.py --check
```

Każdy pack: `tellmesh/{pack}/markpacts/{pack}.markpact.md` — bez duplikacji `handlers.py`.

UriContract (spec) vs UriPack (runtime):

```bash
# spec z manifest.yaml (waliduje się, nie compile'uje do runtime)
urisys markpact gen-contract urikvm/urikvm/manifest.yaml --out markpacts/urikvm.contract.markpact.md
urisys markpact check-drift urikvm/urikvm/manifest.yaml markpacts/urikvm.contract.markpact.md

# runtime → .markpact/ (thin: python:// z repo; full: osadzony kod + proto z uricore)
urisys markpact materialize markpacts/urikvm.markpact.md --root .markpact
urisys markpact pack urikvm --out urikvm.full.markpact.md   # self-contained, bez pip install
urisys markpact run markpacts/urikvm.markpact.md --as pack
```

CI (drift + walidacja):

```bash
python3 scripts/generate_pack_markpacts.py --check
python3 scripts/check_contract_drift.py
bash scripts/validate-all-markpacts.sh
bash scripts/run-markpact-ci.sh
```

Showcase (mock, ręczny):

```bash
SHOWCASE="$(markpact_contracts_packs)/uribrowser.showcase.markpact.md"
urisys markpact analyze "$SHOWCASE"
urisys markpact run-flow "$SHOWCASE#open-and-read" --approve --dry-run
urisys markpact run-flow "$SHOWCASE#install-and-verify" --approve --dry-run
# integracja: sibling repos (TELLMESH_ROOT) albo pip:
# urisys markpact run-flow "$SHOWCASE#install-and-verify" --approve --dry-run --auto-install
```

Skrypt smoke: ``examples/markpact/showcase-run-flow.sh`` (ustawia ``TELLMESH_ROOT``).

Wywołanie URI bez instalowania paczki:

```bash
urisys --packs none \
  --markpact "$PACK" \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve \
  --dry-run
```

Server URI z Markpact:

```bash
urisys --packs none \
  --markpact "$(markpact_contracts_packs)/urisystemd.markpact.md" \
  serve --port 8789
```

HTTP call:

```bash
curl -X POST http://127.0.0.1:8789/uri/call \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "systemd://unit/docker.service/query/status",
    "payload": {},
    "context": {"environment": "real"}
  }'
```

## Przepływ runtime

```text
*.markpact.md
  ↓ parse formalnych bloków
validate UriPack schema
  ↓ compile/cache
.urisys/cache/markpacts/<pack>/<hash>/manifest.yaml
.urisys/cache/markpacts/<pack>/<hash>/<module>/*.py
  ↓ runtime
URI → registry → policy → handler → event JSONL → result
```

## Zasady bezpieczeństwa

Markpact z handlerem Python jest kodem wykonywalnym. Dlatego:

1. Ładuj tylko pliki zaufane albo uruchamiaj je w sandboxie/kontenerze.
2. Działania mutujące oznaczaj `side_effects: true` i `approval: required`.
3. Realne operacje systemowe są domyślne. Symulację włącz przez `--dry-run` lub `--environment mock`.
4. Nie rób automatycznego `pip install` zależności z Markpact bez zgody.
5. W produkcji używaj `urisys markpact compile` i uruchamiaj wygenerowany cache/artefakt.

## Kiedy Markpact zamiast folderu paczki?

Użyj Markpact, gdy:

- chcesz szybko opisać nowy URI pack,
- pack ma kilka tras i kilka handlerów,
- chcesz wygenerować paczkę przez LLM,
- chcesz łatwo reviewować capability, policy, kod i testy w jednym pliku.

Użyj normalnej paczki `uri*`, gdy:

- implementacja ma wiele plików,
- potrzebujesz zależności, assetów, plików binarnych albo dużych adapterów,
- tworzysz stabilny pack produkcyjny.

Najlepszy kompromis to:

```text
Markpact jako źródło → compile → materializowany runtime
```

Release chain (kontrakt → GitHub OCI → markpact.com catalog): [`DISTRIBUTION.md`](DISTRIBUTION.md).
