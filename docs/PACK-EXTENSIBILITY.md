# Rozszerzanie urisys-node — nowe schematy URI (np. `imgl://`, `vql://`)

Jak dodać capability pack do slave node bez restartu procesu (hot-load) i co dzieje się po restarcie komputera.

Powiązane: [`README.md`](README.md) · [`NODE-SETUP.md`](NODE-SETUP.md) · [`DISTRIBUTION.md`](DISTRIBUTION.md) · [`PACKAGES.md`](PACKAGES.md).

## Model trzech warstw

| Warstwa | Co robi | Przykład |
|---------|---------|----------|
| **pip / wheel** | Instalacja kodu w venv (trwałe na dysku) | `urihim`, `uriimgl` |
| **hot-load (pack)** | Rejestracja tras w działającym procesie | `POST /uri/pack {"pack":"him"}` |
| **hot-load (release)** | OCI worker + forward z kontraktu | `POST /uri/pack {contract,version,catalog}` |
| **lazy install** | pip + hot-load przy pierwszym URI | pierwsze `him://…` |
| **boot `release_forwards`** | auto hot-load release przy starcie node | config JSON / env |

```text
pip install wheel  →  import modułu  →  pack.register(runtime)  →  runtime.routes
```

## Wbudowane packi (wheel `urisys`)

Domyślnie przy starcie (`URISYS_NODE_PACKS=node,screen,shell`):

| Pack | Schemat | Moduł |
|------|---------|-------|
| `node` | `node://` | `urisysnode.routes` |
| `screen` | `screen://` | `uriscreen.routes` |
| `shell` | `shell://` | `urishell.routes` |

## Packi opcjonalne (lazy / hot-load)

Mapowanie w `urisysnode/pack_resolver.py`:

| Pack | Schemat | Moduł | PyPI / GitHub |
|------|---------|-------|---------------|
| `kvm` | `kvm://` | `urikvm` | PyPI + GitHub |
| `him` | `him://` | `urihim` | GitHub (auto) |
| `ocr` | `ocr://` | `uriocr` | GitHub (auto) |
| `llm` | `llm://` | `urillm` | GitHub (auto) |

**Nowy schemat (np. `imgl://`) nie działa out-of-the-box** — trzeba dodać wpis w `PACK_MODULES` i `SCHEME_TO_PACK` (lub użyć forward workera).

## Kontrakt packa in-process

Każdy wheel musi eksportować:

```python
def register(runtime):
    runtime.register(
        "imgl://{host}/image/latest/query/layout",
        "python://uriimgl.handlers:layout",
        kind="query",
        operation="imgl.layout",
    )
```

Handler: `def layout(payload, context) -> dict` — `context["config"]`, `context["allow_real"]`, `context["state"]["latest_screen"]` z `uriscreen`.

## Trzy sposoby dodania packa

### A — In-process (jak `urihim`)

1. Paczka Python (`uriimgl`) z `register()`.
2. Wpis w `pack_resolver.py`: `PACK_MODULES`, `SCHEME_TO_PACK`, `PACK_PYPI` / GitHub.
3. Release wheel (PyPI lub GitHub Releases).
4. Na node:
   - lazy przy pierwszym `imgl://…`, lub
   - `node://local/command/install-pack` + `{"pack":"imgl"}`, lub
   - `POST /uri/pack` z `{"pack":"imgl","install":false}` po wcześniejszym `shell://pip`.

### B — Forward worker (bez pip w node)

Dla ciężkich zależności (`rest2imgl`, `rest2vql`):

```python
register_forward_pack(
    runtime,
    scheme="imgl",
    endpoint="http://127.0.0.1:8219",
    patterns=["imgl://{host}/image/latest/query/layout", ...],
)
```

Node proxy’uje do workera (`urisysnode/forward.py`). Worker startuje osobno (systemd, Docker OCI).

**Autostart forwardów** — wpis w `URISYS_NODE_CONFIG`:

```json
{
  "forwards": [
    {
      "scheme": "imgl",
      "endpoint": "http://127.0.0.1:8219",
      "patterns": ["imgl://{host}/image/latest/query/layout"]
    }
  ]
}
```

Alternatywy: env `URISYS_NODE_FORWARDS` (JSON array) lub `URISYS_NODE_FORWARDS_FILE`. Przykład lenovo: [`urisys-node/config/node-profile.lenovo.json`](../../urisys-node/config/node-profile.lenovo.json).

**Release auto-wire** (Markpact + OCI) — wpis w config:

```json
{
  "release_forwards": [
    {
      "contract": "urikvm.contract",
      "version": "0.1.5",
      "catalog": "https://markpact.com",
      "profile": "config/node-profile.json"
    }
  ]
}
```

Alternatywa: env `URISYS_NODE_RELEASE_FORWARDS` (JSON array). Node wywołuje `hotload_release_pack()` przy starcie (best-effort). Szczegóły: [`DISTRIBUTION.md`](DISTRIBUTION.md).

### C — `shell://pip` + hot-load (bez release urisys)

Gdy pack jest już w `PACK_MODULES`:

```bash
# pip wheel z GitHub
curl -X POST http://NODE:8790/uri/call -d '{
  "uri":"shell://pip",
  "payload":{"args":["install","-U","https://github.com/.../uriimgl-....whl"]},
  "context":{"approved":true,"allow_real":true}
}'

# hot-load bez restartu node
curl -X POST http://NODE:8790/uri/pack -d '{"pack":"imgl","install":false}'
```

## API hot-load

| Endpoint / URI | Opis |
|----------------|------|
| `POST /uri/pack` | `{"pack":"him"}` — lokalny pack; `{"contract":"…","version":"…"}` — release OCI |
| `node://local/command/install-pack` | to samo przez URI (wymaga `approved`); `force: true` po `pip install -U` |
| `node://local/command/register-forward` | hot-load forward workera (`scheme`, `endpoint`, `patterns`) |
| `node://local/query/packs` | `loaded` + `available` |
| `GET /uri/routes` | wszystkie zarejestrowane wzorce |

Release hot-load wymaga sparowanego node (`require_paired`). Opcjonalnie: `URISYS_NODE_REQUIRE_SIGNATURE=1` + `URISYS_NODE_TRUSTED_KEYS`.

Wymaga `URISYS_NODE_ALLOW_PACK_LOAD=1` (domyślnie włączone z auto-install).

## Po restarcie komputera

| Co | Zachowanie |
|----|------------|
| Wheels w venv (`urihim`, …) | **Zostają** — `pip install` trwały |
| Proces `urisys node serve` | **Trzeba uruchomić** (systemd / ręcznie) |
| Trasy hot-load w RAM | **Znikają** — node startuje z `URISYS_NODE_PACKS` |
| Lazy przy pierwszym URI | Pack wraca automatycznie (pip skip + register) |

**Restart node** potrzebny tylko po `pip install -U urisys` (nowy kod w wheelu).

## Autostart (systemd user — lenovo / Wayland)

Przykład: [`urisys-node/systemd/urisys-node-user.service`](../urisys-node/systemd/urisys-node-user.service)

```bash
cp urisys-node/systemd/urisys-node-user.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now urisys-node.service
loginctl enable-linger "$USER"   # node bez aktywnej sesji GUI
```

## Ekosystem zewnętrzny (planowane packi)

| Repo | Schemat | Rola w pipeline | Integracja |
|------|---------|-------------------|------------|
| [semcod/imgl](https://github.com/semcod/imgl) | `imgl://` | layout + OCR + click targets | forward `rest2imgl` lub `uriimgl` in-process |
| [oqlos/vql](https://github.com/oqlos/vql) | `vql://` | UI detect, fingerprint, compare | forward `rest2vql` lub pack po `screen://` |

Rekomendowany pipeline:

```text
screen://  →  imgl:// (layout)  →  him:// (click/type)
              vql:// (compare)     opcjonalna weryfikacja UI
```

Capture zostaje w **`uriscreen`** — imgl/vql analizują PNG z `latest_screen`, nie duplikują portal/vdisplay.

## Roadmap (entry points)

Docelowo: discovery packów przez `[project.entry-points."urisys.pack"]` w wheelu — bez edycji `pack_resolver.py`. Do tego czasu: wpis w resolverze lub forward worker.
