# Markpact sources

## Canonical (thin, generated)

```text
tellmesh/{pack}/markpacts/{pack}.markpact.md
```

Generated from each pack's `manifest.yaml` — handlers stay as `python://` in the repo (no duplication).

```bash
cd tellmesh/urisys
python3 scripts/generate_pack_markpacts.py
python3 scripts/generate_pack_markpacts.py --check          # CI drift
python3 scripts/generate_pack_markpacts.py --aggregate      # copy → markpact-contracts/packs/
bash scripts/run-markpact-ci.sh                             # drift + validate + tests
```

Run / unpack in cwd:

```bash
cd tellmesh/urikvm
export TELLMESH_ROOT=~/github/tellmesh
urisys markpact run markpacts/urikvm.markpact.md --as flow --approve --dry-run
urisys markpact run markpacts/urikvm.markpact.md --as pack
```

## Aggregates & legacy

| Path | Role |
|------|------|
| `tellmesh/markpact-contracts/packs/*.markpact.md` | Aggregated thin copies (optional) |
| `markpact-contracts/packs/uribrowser.showcase.markpact.md` | Manual integration demo (`run-flow`) |
| `markpact-contracts/packs/legacy/*.showcase.markpact.md` | Archived thick drafts — do not use |

When `urisys` lives in `tellmesh/urisys`, `scripts/paths.sh` resolves `markpact-contracts/packs` automatically.

## Docker / lab Markpacts

Contract and bundle Markpacts stay in their packages:

```text
urirdp-docker/markpacts/
uristepper-docker/markpacts/
urisys-automation-lab/markpacts/
urisys-node/markpacts/
urienv-docker/markpacts/
```

## Validate

```bash
source scripts/paths.sh
urisys markpact validate "$(markpact_contracts_packs)/uribrowser.markpact.md"
bash scripts/validate-all-markpacts.sh
```

## Standalone urisys clone

If `../markpact-contracts` is missing, clone it next to urisys or set:

```bash
export MARKPACT_CONTRACTS_PACKS=/path/to/markpact-contracts/packs
export TELLMESH_ROOT=/path/to/tellmesh   # for python:// handlers + drift --check
```

See [`docs/MARKPACT.md`](../docs/MARKPACT.md) for full command reference.
