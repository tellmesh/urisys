# Model danych urisys — gdzie co jest trzymane

Trzy warstwy: **konfiguracja** (statyczna, co node MA robić), **dane runtime**
(zmienne, co node WYGENEROWAŁ) i **sesje** (in-memory + natywne profile przeglądarek).

Powiązane: [`NODE-SETUP.md`](NODE-SETUP.md) (instalacja slave), [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Zasada podziału

```text
~/.config/urisys/          → co node MA robić   (profil, node.env, secrets.env)
~/.local/share/urisys/     → co node WYGENEROWAŁ (identity, pairing, events, captures)
~/.config/google-chrome/   → sesje WWW (LinkedIn, Google) — poza urisys
~/venv/ (lub site-packages)→ kod i packi Python
```

Repo trzyma **szablony** (`urisys-node/config/`), nigdy runtime danych.

## 1. Konfiguracja (statyczna, wersjonowana)

| Co | Zmienna / ścieżka | Uwaga |
|---|---|---|
| Profil node (driver, policy, output_dir) | `URISYS_NODE_CONFIG` → `~/.config/urisys/node-profile.json` | kopia szablonu `node-profile.lenovo.json` |
| Env startowe | `~/.config/urisys/node.env` | format **systemd EnvironmentFile** (`KEY=value`, bez `export`/`$HOME`) |
| Sekrety (API keys, SMTP) | `~/.config/urisys/secrets.env` (chmod 600) | **nie** w JSON, **nie** w git |
| Route-map / rejestr nodów (kontroler) | `urisys-node/config/route-map.*.yaml` | tylko na master/dev |

## 2. Dane runtime (zmienne, generowane)

Root: **`URISYS_NODE_DATA`**. Domyślnie **`~/.local/share/urisys`** (XDG —
`default_data_root()` w `urisysnode/identity.py`), niezależnie od CWD startu.
Wcześniej domyślał do `data/` względem CWD — to był footgun (start z innego
katalogu → nowa tożsamość, utrata pairingu).

```text
~/.local/share/urisys/
├── node-identity.json   # node_id, fingerprint
├── node-pairing.json    # enrollment z kontrolerem
├── events.jsonl         # audit log URI (append-only; URISYS_NODE_EVENTS)
├── screens/             # screen:// capture       (screen.output_dir)
├── office/              # urioffice:// output      (office.output_dir)
└── browser/             # browser:// screenshots   (URISYS_BROWSER_SCREEN_DIR)
```

Precedencja ścieżek: `URISYS_NODE_DATA` > `$XDG_DATA_HOME/urisys` > `~/.local/share/urisys`.

## 3. Sesje aplikacyjne (in-memory — NIE persystowane)

W `runtime.state` (RAM, jeden proces node): `browser_sessions`, `mail_drafts`,
`latest_screen`. Po restarcie znikają — zamierzone. Trwałość wymagałaby zapisu do
`URISYS_NODE_DATA/sessions/`.

## 4. Sesje przeglądarek (logowania) — poza urisys

urisys nie przechowuje cookies/loginów. Są w natywnym profilu:

| Przeglądarka | Profil |
|---|---|
| Chrome | `~/.config/google-chrome/Default` |
| Chromium | `~/.config/chromium/Default` |
| Firefox | `~/.mozilla/firefox/<profile>/` |

Dla automatyzacji: `URISYS_BROWSER_USER_DATA_DIR=$HOME/.config/google-chrome/Default`.

## 5. Setup slave (lenovo)

Gotowe szablony w `urisys-node` (sibling repo): `config/node.env.example` +
`systemd/urisys-node-user.service` ustawiają powyższy układ. Skrót:

```bash
mkdir -p ~/.config/urisys ~/.local/share/urisys/{screens,office,browser}
cp config/node.env.example         ~/.config/urisys/node.env
cp config/node-profile.lenovo.json ~/.config/urisys/node-profile.json
```

systemd unit ustawia `URISYS_NODE_DATA`/`EVENTS`/`CONFIG`/`BROWSER_USER_DATA_DIR`
przez `%h` + ładuje `node.env`/`secrets.env` jako `EnvironmentFile`.
