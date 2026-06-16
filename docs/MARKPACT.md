# UriPack Markpact

`UriPack Markpact` to jednoplikowy format paczki URI dla `urisys`. Służy do szybkiego tworzenia cienkich warstw nad usługą, urządzeniem, stroną WWW albo procesem bez budowania pełnej paczki Python/JS.

Najważniejsza zasada:

```text
Markpact = format autorski i dystrybucyjny
cache runtime = wygenerowany manifest + wyciągnięte handlery
urisys = kontrolery, managery, routing, policy, eventy, flow
```

Nie należy traktować Markdowna jako bezpośredniego formatu produkcyjnego. `urisys` czyta tylko formalne bloki `markpact:*`, waliduje je i materializuje do cache.

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
| `markdown markpact:docs` | Dokumentacja użytkowa wyciągana do cache. |
| `js markpact:handler id=<id>` | Źródło JS dla przyszłego `urisys-js`; Python runtime go nie wykonuje. |

## Komendy

```bash
source scripts/paths.sh
PACK="$(markpact_contracts_packs)/uribrowser.markpact.md"

urisys markpact validate "$PACK"
urisys markpact compile "$PACK"
urisys markpact routes "$PACK"
urisys markpact test "$PACK"
```

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
