# Bootstrap lenovo — tylko `pip install urisys`, potem URI

Po `pip install urisys` wystarczy:

```text
urisys node serve --host 0.0.0.0 --port 8790
```

Node startuje z **`node` + `screen` + `shell`** (wbudowane w wheel). Packi **kvm/him/ocr/llm** instalujesz przez:

1. **lazy install** przy pierwszym URI (`him://`, …), albo
2. **`shell://pip`** z GitHub Releases (gdy PyPI niedostępne)

## Bootstrap packów przez shell:// (bez PyPI)

Z hosta (route-map → lenovo):

```bash
curl -sS -X POST http://192.168.188.201:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"shell://pip","payload":{"args":["install","-U","https://github.com/tellmesh/urihim/releases/download/v0.1.2/urihim-0.1.2-py3-none-any.whl"]},"context":{"approved":true,"allow_real":true}}'
```

Flow (wszystkie packi z GitHub):

```bash
# na node z urishell — lokalnie lub przez forward
urisys --packs shell flow urisys-node/flows/bootstrap-kvm-github.uri.flow.yaml --approve --allow-real
```

Z mastera przez route-map:

```bash
urisys-node call "shell://pip" \
  --payload '{"args":["install","-U","https://github.com/tellmesh/urihim/releases/download/v0.1.2/urihim-0.1.2-py3-none-any.whl"]}' \
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

## Stary sposób (dev monorepo)

`bash scripts/install-kvm-packs-editable.sh` — tylko CI/dev z git checkout.
