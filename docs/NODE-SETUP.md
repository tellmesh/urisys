# Bootstrap lenovo — tylko `pip install urisys`, potem URI

Po `pip install urisys` wystarczy:

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
  --route-map urisys-node/config/route-map.lenovo.yaml \
  --nodes-registry urisys-node/config/nodes.registry.json
```

Po `pip install` packów zrób hot-load (bez restartu):

```bash
curl -sS -X POST http://192.168.188.201:8790/uri/pack \
  -H 'Content-Type: application/json' \
  -d '{"pack":"him","install":false}'
```

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
pip install -U urisysedge urikvm
```

Pierwsze `screen://…/capture` z `allow_real: true` doinstaluje `mss` i `Pillow`.

## Co nadal wymaga PyPI / GitHub

| Pack | PyPI | GitHub Releases |
|------|------|-----------------|
| urisysedge, urikvm | ✅ | opcjonalnie |
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
| `URISYS_NODE_CONFIG` | `config/node-profile.json` | Profil `him`, `screen`, policy |

## Stary sposób (dev monorepo)

`bash scripts/install-kvm-packs-editable.sh` — tylko CI/dev z git checkout.

## Rozwiązywanie problemów (lenovo)

### `ModuleNotFoundError: No module named 'uri_control'`

Moduł `uri_control` jest **w pakiecie PyPI `uricore`** (nie instaluj go osobno). Błąd oznacza zwykle:

1. **`urisys` bez zależności** — stara instalacja (`0.1.16` w `~/.local`, Python 3.14) bez `uricore`
2. **Zły interpreter** — `urisys` z 3.14, a pracujesz w 3.12 (Jupyter/inne)
3. **Zła komenda** — na slave potrzebujesz **`urisys node serve`**, nie samo `urisys serve`

**Naprawa (zalecany venv Python 3.12):**

```bash
python3.12 -m venv ~/venv
source ~/venv/bin/activate
pip install -U pip
pip install -U uricore urisysedge "urisys[real]"

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

**Usuń zepsutą instalację 3.14 (opcjonalnie):**

```bash
python3.14 -m pip uninstall -y urisys urisysedge uricore
rm -f ~/.local/bin/urisys ~/.local/bin/urisys-node
```

### `urisys serve` vs `urisys node serve`

| Komenda | Cel |
|---------|-----|
| `urisys node serve` | **Slave desktop** — screen, him, lazy packi (:8790) |
| `urisys serve` | Prosty HTTP server packów (dev); na lenovo zwykle **nie** to |
