# Bootstrap lenovo — tylko `pip install urisys`, potem URI

Po `pip install urisys` wystarczy:

```text
urisys node serve --host 0.0.0.0 --port 8790
```

Node startuje z **`node` + `screen`** (wbudowane w wheel). Packi **kvm/him/ocr/llm** i backendy **`[real]`** (mss, pyautogui, …) instalują się **automatycznie przy pierwszym URI**, jeśli `URISYS_NODE_AUTO_INSTALL=1` (domyślnie przy `urisys node serve`).

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

## Co nadal wymaga PyPI

| Pack | PyPI |
|------|------|
| urisysedge, urikvm | ✅ |
| urihim, uriocr, urillm | 🔲 (auto-install zwróci błąd pip do publikacji) |

## Stary sposób (dev monorepo)

`bash scripts/install-kvm-packs-editable.sh` — tylko CI/dev z git checkout.
