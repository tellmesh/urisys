# Bootstrap lenovo — `urisys init`, potem node

> Gdzie node trzyma dane (identity, pairing, events, captures) i jak ustawić
> ścieżki: [`DATA-MODEL.md`](DATA-MODEL.md). Skrót: runtime → `~/.local/share/urisys`
> (XDG, niezależnie od CWD), config → `~/.config/urisys/`.

## Jedna komenda (zalecane)

Na świeżym venv lub po błędzie `ModuleNotFoundError: uri_control`:

```bash
python3.12 -m venv ~/venv && source ~/venv/bin/activate
pip install -U "urisys>=0.1.36"
urisys init
source ~/.config/urisys/node.env
urisys node serve --host 0.0.0.0 --port 8790
```

> **Bez hasła GitHub:** `urisys init` instaluje z **publicznych wheels** (uricore + urisys-node z GitHub Releases), nie `git+https://`.
> Override: `URISYS_NODE_WHEEL_URL`, `URISYS_NODE_PIP_SPEC`, `URISYS_URICORE_WHEEL_URL`.

Wheel **musi** nazywać się `urisys_node-{ver}-py3-none-any.whl` (podkreślnik) — pip odrzuca `urisys-node-…` jako invalid version.

> **Uwaga:** PyPI pakiet `uricore` to **inny projekt** (moduł `uricore/`, nie `uri_control/`).
> `urisys init` instaluje tellmesh uricore z GitHub wheel i naprawia złą instalację automatycznie.

`urisys init` wykonuje:

1. `pip install -U pip` + tellmesh **uriresolver** + **uricore** wheels + `urisys[real]`
2. opcjonalnie urisys-node wheel z GitHub Releases (osobny krok; warn jeśli brak release)
3. jeśli wykryje zły PyPI `uricore` → `pip uninstall` + wheel z GitHub
3. weryfikację `import uri_control`
4. `urisys doctor`
5. zapis `~/.config/urisys/node.env` z `URISYS_ALLOW_REAL=1` i `URISYS_NODE_AUTO_INSTALL=1`

Ręczna naprawa (gdy init niedostępny):

```bash
pip uninstall -y uricore
pip install -U https://github.com/tellmesh/uricontrol/releases/download/v0.1.8/uricore-0.1.8-py3-none-any.whl
python -c "import uri_control; print('OK')"
```

Opcje: `--dry-run`, `--skip-pip`, `--no-write-env`, `--profile dev`.

**Bootstrap na konsoli lenovo** (gdy SSH niedostępne z dev): [`scripts/bootstrap-lenovo-local.sh`](../scripts/bootstrap-lenovo-local.sh)

```bash
bash scripts/bootstrap-lenovo-local.sh
# wheel urisys-node: https://github.com/tellmesh/urisys-node/releases/download/v0.1.3/urisys_node-0.1.3-py3-none-any.whl
```

---

Po `pip install urisys` (z pełnymi zależnościami) wystarczy:

```text
urisys node serve --host 0.0.0.0 --port 8790
```

Node startuje z **`node` + `screen` + `shell`** (wbudowane w wheel). Packi **kvm/him/ocr/llm** instalujesz przez:

1. **lazy install** przy pierwszym URI (`him://`, …), albo
2. **`shell://pip`** z GitHub Releases (gdy PyPI niedostępne), albo
3. **`node://…/command/install-pack`** / **`POST /uri/pack`** (hot-load)

Pełny opis rozszerzeń (np. `imgl://`, `vql://`): [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md).

**Wayland (GNOME):** `him://` z pyautogui nie działa — ustaw driver ydotool:

```bash
sudo apt install ydotool   # + ydotoold (uinput)
export URISYS_HIM_DRIVER=ydotool
# lub w profile JSON: {"him": {"driver": "ydotool"}}
```

Na Wayland z zainstalowanym `ydotool` driver wybiera się **automatycznie** (`WAYLAND_DISPLAY`).

## Autostart po restarcie komputera

Wheels z `pip install` **zostają** w venv. Proces node **nie** — uruchom ponownie lub użyj systemd.

**Ręcznie:**

```bash
export URISYS_ALLOW_REAL=1
export URISYS_NODE_CONFIG=/home/tom/urisys-node-profile.json   # opcjonalnie
~/venv/bin/urisys-node serve --host 0.0.0.0 --port 8790
```

**systemd (user):** [`urisys-node/systemd/urisys-node-user.service`](../urisys-node/systemd/urisys-node-user.service)

```bash
cp urisys-node/systemd/urisys-node-user.service ~/.config/systemd/user/urisys-node.service
systemctl --user daemon-reload && systemctl --user enable --now urisys-node.service
loginctl enable-linger "$USER"
```

Po starcie node packi opcjonalne wracają przy **pierwszym URI** (lazy) lub jednym `install-pack` — restart node **nie** jest potrzebny, chyba że zrobiłeś `pip install -U urisys`.

**Upgrade z dev maszyny (urisys 0.1.24 + urihim 0.1.3):** [`scripts/deploy-lenovo-node.sh`](../scripts/deploy-lenovo-node.sh)

## Bootstrap packów przez shell:// (bez PyPI)

Z hosta (route-map → lenovo):

```bash
curl -sS -X POST http://192.168.188.201:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"shell://pip","payload":{"args":["install","-U","https://github.com/tellmesh/urihim/releases/download/v0.1.3/urihim-0.1.3-py3-none-any.whl"]},"context":{"approved":true,"allow_real":true}}'
```

Flow (wszystkie packi z GitHub):

```bash
# na node z urishell — lokalnie lub przez forward
urisys --packs shell flow urisys-node/flows/bootstrap-kvm-github.uri.flow.yaml --approve --allow-real
```

Z mastera przez route-map:

```bash
urisys-node call "shell://pip" \
  --payload '{"args":["install","-U","https://github.com/tellmesh/urihim/releases/download/v0.1.3/urihim-0.1.3-py3-none-any.whl"]}' \
  --approve --allow-real \
  --route-map ../../urisys-node/config/route-map.lenovo.yaml \
  --nodes-registry ../../urisys-node/config/nodes.registry.json
```

Po `pip install` packów zrób hot-load (bez restartu):

```bash
curl -sS -X POST http://192.168.188.201:8790/uri/pack \
  -H 'Content-Type: application/json' \
  -d '{"pack":"him","install":false}'
```

### Hot-load z release (OCI worker, bez pip)

Gdy capability jest w osobnym kontenerze (markpact.com + GitHub Release assets):

```bash
curl -sS -X POST http://192.168.188.201:8790/uri/pack \
  -H 'Content-Type: application/json' \
  -d '{"contract":"urikvm.contract","version":"0.1.5","catalog":"https://markpact.com"}'
```

Wymaga: node **sparowany** z kontrolerem. Opcjonalnie weryfikacja podpisu: `URISYS_NODE_REQUIRE_SIGNATURE=1`. Szczegóły: [`DISTRIBUTION.md`](DISTRIBUTION.md).

Wyłączenie auto-install:

```text
urisys node serve --no-auto-install
```

## Instalacja packa przez URI (bez skryptów)

```bash
curl -sS -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"node://local/command/install-pack","payload":{"pack":"kvm"},"context":{"approved":true}}'
```

Lista załadowanych packów:

```bash
curl -sS -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"node://local/query/packs","payload":{},"context":{}}'
```

## Lazy load przy pierwszym wywołaniu

Pierwsze `kvm://…` (z `approved`) uruchomi w tle:

```text
pip install -U uricore urikvm
```

Pierwsze `screen://…/capture` z `allow_real: true` doinstaluje `mss` i `Pillow`.

## Co nadal wymaga PyPI / GitHub

| Pack | PyPI | GitHub Releases |
|------|------|-----------------|
| uriresolver, uriguard, uricontrol, urikvm | ✅ | opcjonalnie |
| urihim | 🔲 | ✅ [v0.1.2](https://github.com/tellmesh/urihim/releases/tag/v0.1.2) |
| uriocr | 🔲 | ✅ [v0.1.0](https://github.com/tellmesh/uriocr/releases/tag/v0.1.0) |
| urillm | 🔲 | ✅ [v0.1.0](https://github.com/tellmesh/urillm/releases/tag/v0.1.0) |

Lazy install (`URISYS_PACK_SOURCE=auto`, domyślnie) pobiera **him/ocr/llm z GitHub Releases**.

## Zmienne środowiska (slave)

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `URISYS_NODE_PACKS` | `node,screen,shell` | Packi ładowane przy starcie node |
| `URISYS_NODE_AUTO_INSTALL` | `1` | Lazy pip przy pierwszym URI |
| `URISYS_NODE_ALLOW_PACK_LOAD` | `1` (gdy auto-install) | `POST /uri/pack` |
| `URISYS_ALLOW_REAL` | `0` | `pyautogui`, portal capture, `shell` subprocess |
| `URISYS_PACK_SOURCE` | `auto` | `pypi` \| `github` \| `auto` |
| `URISYS_NODE_CONFIG` | `config/node-profile.json` | Profil `him`, `screen`, policy, `release_forwards` |

## Stary sposób (dev monorepo)

`bash scripts/install-kvm-packs-editable.sh` — tylko CI/dev z git checkout.

## Rozwiązywanie problemów (lenovo)

### `ModuleNotFoundError: No module named 'uri_control'`

Moduł `uri_control` jest **w pakiecie PyPI `uricore`** (nie instaluj go osobno). Błąd oznacza zwykle:

1. **`urisys` bez zależności** — stara instalacja (`0.1.16` w `~/.local`, Python 3.14) bez `uricore`
2. **Zły interpreter** — `urisys` z 3.14, a pracujesz w 3.12 (Jupyter/inne)
3. **Zła komenda** — na slave potrzebujesz **`urisys node serve`**, nie samo `urisys serve`

**Szybka naprawa (ten sam Python 3.14, bez venv):**

```bash
python3.14 -m pip install -U uriresolver uricore "urisys[real]"
urisys doctor    # od urisys ≥0.1.30 działa nawet gdy coś dalej brakuje
urisys serve --help
```

**Naprawa zalecana (venv Python 3.12):**

```bash
python3.12 -m venv ~/venv
source ~/venv/bin/activate
pip install -U pip
pip install -U uriresolver uricore "urisys[real]"

# weryfikacja (nowe)
urisys doctor
urisys node serve --help

# start node (Wayland)
export URISYS_ALLOW_REAL=1
export URISYS_NODE_AUTO_INSTALL=1
urisys node serve --host 0.0.0.0 --port 8790
```

`GET /health` zwraca też: `urisys`, `uricore`, `python`, `python_executable`, `packs_loaded`, `him_driver`.

**Upgrade z dev (LAN, gdy node już działa):** [`scripts/deploy-lenovo-node.sh`](../scripts/deploy-lenovo-node.sh)

### Zdalne operacje z hosta dev (`urisys remote`)

Wymaga **`urisys-node>=0.1.10`** w tym samym venv (port takeover + brak legacy `urisysedge`):

```bash
pip install -U urisys urisys-node   # lub: urisys init
urisys doctor                       # check urisys_node_version

urisys remote health --endpoint http://192.168.188.201:8790
urisys remote restart --endpoint http://192.168.188.201:8790
urisys remote wait --timeout 60
urisys remote call "node://lenovo/query/workers"
urisys remote restart-worker browser
urisys remote upgrade-node
```

`urisys remote` deleguje do `urisys-node remote` (ten sam route-map: `urisys-node/config/route-map.lenovo.yaml`).
`restart` zabija listener na porcie (`fuser -k`) i uruchamia `urisys node serve` w tle na slave.
Przerwanie połączenia HTTP po `restart` jest **oczekiwane** — sprawdź `urisys remote wait`.

### Lenovo: `pip install -U urisys-node` zostaje na 0.1.3

PyPI ma starą wersję (z `urisysedge`). **`urisys init`** i **`urisys node serve`** (auto-install) wybierają **nowszą** wersję z GitHub Releases niż PyPI (`version_resolve`).

Na slave (lenovo):

```bash
source ~/venv/bin/activate
pip uninstall -y urisysedge urisys-node
urisys init
# albo ręcznie:
pip install -U "$(python -c 'from urisys.node_install import pip_spec; print(pip_spec())')"

fuser -k 8790/tcp 2>/dev/null || true
urisys node serve --host 0.0.0.0 --port 8790
```

`urisys doctor` → **fail** na `urisys_node_version` dopóki nie ma ≥0.1.22.

Stary `urisys-node 0.1.3` pada z `ModuleNotFoundError: urisysedge` — nie używaj go.

**Usuń zepsutą instalację 3.14 (opcjonalnie):**

```bash
python3.14 -m pip uninstall -y urisys uricore uriresolver
rm -f ~/.local/bin/urisys ~/.local/bin/urisys-node
```

### Test zgodności Python (3.10–3.14)

```bash
bash scripts/test-python-matrix.sh          # lokalnie: venv per dostępna wersja
python3 -m pytest tests/test_python_compat.py tests/test_bootstrap.py -q
```

CI: `.github/workflows/python-compat.yml` (macierz 3.10–3.13 + unit bootstrap/doctor).

### `urisys serve` vs `urisys node serve` vs `urisys remote`

| Komenda | Cel |
|---------|-----|
| `urisys node serve` | **Slave desktop** — screen, him, lazy packi (:8790) |
| `urisys remote …` | **Dev → slave** — health, restart, call URI, workers (wymaga `urisys-node`) |
| `urisys serve` | Prosty HTTP server packów (dev); na lenovo zwykle **nie** to |
