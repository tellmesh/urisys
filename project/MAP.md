# Przewodnik po `project/map.toon.yaml`

Plik [`map.toon.yaml`](map.toon.yaml) jest **generowany automatycznie** przez `code2llm ./ -f all`.  
Nie edytuj go ręcznie — aktualizuj dokumentację w `docs/` i kod; mapę regeneruj po większych zmianach.

## Nagłówek (linie 1–6)

```yaml
# urisys | 243f 14958L | yaml:36,shell:41,... | 2026-06-16
# stats: 581 func | 0 cls | 243 mod | CC̄=3.9 | critical:26 | cycles:0
# alerts[5]: fan-out main=41; CC analyze_run=34; ...
# hotspots[5]: main fan=41; MarkpactManager.compile fan=34; ...
```

| Pole | Znaczenie |
|------|-----------|
| `243f` | 243 pliki źródłowe |
| `14958L` | ~15k linii kodu |
| `581 func` | funkcje/metody |
| `CC̄=3.9` | średnia cyclomatic complexity |
| `alerts` | przekroczenia limitów (fan-out, CC) |
| `hotspots` | moduły z największym coupling |

## Sekcja `M[]` — mapa modułów

Format: `ścieżka/względna,liczba_linii`

Grupy logiczne (wg prefiksów):

| Prefix | Moduły | Rola |
|--------|--------|------|
| `src/urisys/` | cli, managers, controllers | Centralny controller |
| `../uricore/` | `uri_control.edge` | ★ Wspólny edge runtime |
| `../uriresolver/` | `uri_resolver` | ★ Intent router + policy |
| `urirdp-docker/` | urirdp_*, urirdpedge | RDP desktop automation |
| `urikvm-docker/` | urikvm, uriocr, urillm | KVM stack |
| `urisys-automation-lab/` | flows, server, lab packs | Lab 10 flows |
| `urisys-node/` | urisysnode, uriscreen | Distributed node |
| `scripts/` | run_test_sessions, session_report | Test harness |
| `local-lab/` | build/publish scripts | markpact.com chain |
| `examples/` | shell, frontend, markpact | Przykłady użycia |

Szczegółowy katalog paczek: [`PACKAGES.md`](PACKAGES.md), [`../docs/PACKAGES.md`](../docs/PACKAGES.md).

## Sekcja `D:` — detale modułów

Dla wybranych plików:

- `e:` — eksportowane symbole
- `ClassName:` — metody klasy
- `function_name()` — funkcje top-level

Przykład użycia — znajdź API flow runnera:

```bash
grep -A5 'flow_runner.py' map.toon.yaml
# → plan_flow, run_flow_file, _step_ok, ...
```

## Powiązane pliki w `project/`

| Plik | Format | Kiedy czytać |
|------|--------|--------------|
| [`calls.yaml`](calls.yaml) / [`calls.mmd`](calls.mmd) | call graph | Zależności między funkcjami |
| [`context.md`](context.md) | Markdown | Wklejka do LLM |
| [`analysis.toon.yaml`](analysis.toon.yaml) | YAML | CC, god functions |
| [`project.toon.yaml`](project.toon.yaml) | YAML | Kompaktowy widok + refactor queue |
| [`duplication.toon.yaml`](duplication.toon.yaml) | YAML | redup scan (wewnątrz wybranych plików) |

## Regeneracja

```bash
cd urisys
code2llm ./ -f all -o ./project
```

Po migracji edge runtime do `uricore` + `uriresolver` uruchom ponownie, żeby zaktualizować `M[]`.

## Hotspoty do refactoru (2026-06-16)

Z nagłówka mapy:

1. `src/urisys/cli.py:main` — fan-out 41  
2. `MarkpactManager.compile` — fan-out 34, CC wysokie  
3. `scripts/run_test_sessions.session_lab_10_flows` — fan-out 31  
4. `scripts/session_report.analyze_run` — CC 34  

Plan: [`planfile-tickets.yaml`](planfile-tickets.yaml), [`planfile.yaml`](../planfile.yaml).
