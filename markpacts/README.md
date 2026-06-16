# Markpact sources

**Canonical pack Markpacts** (uribrowser, uridocker, …) live in the sibling repo:

```text
tellmesh/markpact-contracts/packs/
```

When `urisys` is checked out inside the tellmesh workspace, validation scripts resolve that path automatically via `scripts/paths.sh`.

Docker- and lab-specific Markpacts stay in their packages:

```text
urirdp-docker/markpacts/
uristepper-docker/markpacts/
urisys-automation-lab/markpacts/
urisys-node/markpacts/
urienv-docker/markpacts/
```

## Examples

```bash
# tellmesh workspace
source scripts/paths.sh
urisys markpact validate "$(markpact_contracts_packs)/uribrowser.markpact.md"

bash scripts/validate-all-markpacts.sh
```

## Standalone urisys clone

If `../markpact-contracts` is missing, clone it next to urisys or set:

```bash
export MARKPACT_CONTRACTS_PACKS=/path/to/markpact-contracts/packs
```
