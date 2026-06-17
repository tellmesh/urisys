# Repozytoria tellmesh — mapowanie paczek

Stan: 2026-06-17. Po migracji **kod packów** żyje w sibling repos obok `urisys/`; monorepo `urisys` trzyma tylko docker glue, testy i skrypty.

Organizacja GitHub: **[tellmesh](https://github.com/tellmesh)** (paczki urisys) · **[semcod](https://github.com/semcod)** (narzędzia dev: goal, code2logic, costs — **nie** duplikaty packów URI).

## Layout workspace

```text
/home/tom/github/tellmesh/
├── urisys/                 glue + CLI (git: tellmesh/urisys)
├── urisysedge/             edge runtime
├── urioperators/           LLM helpers
├── urisys-node/            urisysnode, uriscreen, urishell
├── urikvm/ urihim/ uriocr/ urillm/
├── urimail/ urioffice/ urivql/
├── urikvmedge/             CLI urisys-kvm
├── urirdp/                 urirdp*, urirdpedge
├── uribrowser/ urienv/ uristepper/
└── urisys-automation-lab/  labedge, stt, chat, …
```

## Git remote (`origin`)

| Katalog tellmesh | Repo GitHub | Uwagi |
|------------------|-------------|--------|
| `urisys` | [tellmesh/urisys](https://github.com/tellmesh/urisys) | monorepo glue |
| `urisysedge` | [tellmesh/urisysedge](https://github.com/tellmesh/urisysedge) | PyPI ✅ |
| `urioperators` | *(brak `.git` lokalnie)* | utwórz `tellmesh/urioperators` |
| `uricore` | [tellmesh/uricore](https://github.com/tellmesh/uricore) | wheel z Releases, nie PyPI squatter |
| `urikvm` | [tellmesh/urikvm](https://github.com/tellmesh/urikvm) | PyPI ✅ |
| `urihim` | [tellmesh/urihim](https://github.com/tellmesh/urihim) | GitHub Releases |
| `uriocr` | [tellmesh/uriocr](https://github.com/tellmesh/uriocr) | GitHub Releases |
| `urillm` | [tellmesh/urillm](https://github.com/tellmesh/urillm) | GitHub Releases |
| `urimail` | [tellmesh/urimail](https://github.com/tellmesh/urimail) | GitHub Releases |
| `urioffice` | [tellmesh/urioffice](https://github.com/tellmesh/urioffice) | GitHub Releases |
| `urivql` | [tellmesh/urivql](https://github.com/tellmesh/urivql) | GitHub Releases |
| urisys-node | *(brak `.git`)* | wheel: `urisys_node-0.1.3-py3-none-any.whl` (PEP 427, **nie** `urisys-node-…`) |
| `urirdp` | *(brak `.git`)* | bundle multi-module |
| `urikvmedge` | *(brak `.git`)* | kvm docker CLI |
| `uribrowser` | *(brak `.git`)* | |
| `urienv` | *(brak `.git`)* | |
| `uristepper` | *(brak `.git`)* | |
| `urisys-automation-lab` | *(brak `.git`)* | |

**Żaden** z powyższych packów URI **nie** ma odpowiednika pod [github.com/semcod](https://github.com/semcod). Semcod hostuje m.in. `goal`, `code2logic`, `imgl`, `costs` — to osobny ekosystem integracji (forward `imgl://`, nie fork `urihim`).

## Brak duplikacji vendored

```bash
cd urisys
python3 scripts/pack_sync.py check --all   # 32 packi OK
find urisys -path '*/packages/python/*' -name handlers.py   # brak wyników
```

## Inicjalizacja slave (bez hasła GitHub)

`urisys init` **nie** używa `git+https://` — tylko publiczne wheels:

| Składnik | Źródło |
|----------|--------|
| uricore | `https://github.com/tellmesh/uricore/releases/download/v0.1.8/...whl` |
| urisysedge | PyPI |
| urisys-node | `https://github.com/tellmesh/urisys-node/releases/download/v0.1.3/urisys_node-0.1.3-py3-none-any.whl` |

Override: `URISYS_NODE_WHEEL_URL`, `URISYS_URICORE_WHEEL_URL`.

Szczegóły: [`DISTRIBUTION.md`](DISTRIBUTION.md) · [`NODE-SETUP.md`](NODE-SETUP.md).

## Utworzenie brakujących repo (dev)

```bash
cd urisys
python3 scripts/pack_sync.py init-repo urisys-node   # scaffold w tellmesh/urisys-node
# potem: git init && git remote add origin git@github.com:tellmesh/urisys-node.git
bash scripts/publish-kvm-packs-github.sh             # Release assets dla him/ocr/llm
```

Powiązane: [`PACKAGES.md`](PACKAGES.md) · [`../scripts/pack_registry.py`](../scripts/pack_registry.py).
