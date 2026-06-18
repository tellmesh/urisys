# `urisys` CLI

## Ładowanie paczek

```bash
export TELLMESH_ROOT=~/github/tellmesh   # opcjonalnie: manifesty z sibling checkout

urisys --packs shell,kvm routes
urisys --packs urikvm routes             # alias → pakiet urikvm
```

Z `TELLMESH_ROOT` (lub auto-wykrycia workspace tellmesh) `PackManager` ładuje `manifest.yaml`
z repozytoriów sibling bez `pip install`. Multi-scheme bundle (np. `urikv` z `schemes: [kv, log]`)
jest pomijany — użyj thin markpactów `urikv-kv` / `urikv-log` albo `--markpact`.

Mock browser (URI `browser://default/page/open`) — Markpact, nie docker pack:

```bash
source scripts/paths.sh
urisys --packs none \
  --markpact "$(markpact_contracts_packs)/uribrowser.markpact.md" \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve --dry-run
```

Produkcyjny pack `browser` → moduł `uribrowserdocker` (`browser://{session}/page/command/open`).

`--packs all` ładuje aliasy z `DEFAULT_PACKAGES` (browser, shell, kvm, env, rdp, screen, …).
Brakujące pakiety są pomijane z ostrzeżeniem.

`--packs none` nie ładuje domyślnych paczek — przydatne z `--markpact`:

```bash
urisys --packs none --markpact "$(markpact_contracts_packs)/uribrowser.markpact.md" routes
```

## Markpact

```bash
urisys markpact validate PATH.markpact.md
urisys markpact compile PATH.markpact.md
urisys markpact materialize PATH.markpact.md --root .markpact
urisys markpact materialize PATH.markpact.md --platforms linux,server,esp32
urisys markpact materialize PATH.markpact.md --no-platform-export
urisys markpact export-platform PATH.markpact.md --out generated
urisys markpact run PATH.markpact.md --as flow --approve --dry-run
urisys markpact run PATH.markpact.md#flow-id --as flow --approve --dry-run
urisys markpact gen-contract path/to/manifest.yaml --out markpacts/pack.contract.markpact.md
urisys markpact check-drift path/to/manifest.yaml markpacts/pack.contract.markpact.md
bash scripts/run-markpact-ci.sh
bash scripts/marksync-materialize.sh markpact-contracts/packs/desktop-automation-processes.markpact.md
MARKSYNC_DEPLOY=1 DEPLOY_DIR=/tmp/edge-process bash scripts/marksync-materialize.sh …
bash scripts/marksync-deploy.sh markpact-contracts/packs/machine-cycle-process.markpact.md
```

### UriProcess — resolver runtime

Resolver YAML **nie** jest w pliku procesu. Ładuj przed `run` / edge serve:

```bash
export TELLMESH_ROOT=~/github/tellmesh
export URISYS_RESOLVER_CONFIG=.markpact/desktop_automation_processes/generated/linux/urisys.runtime.yaml

urisys markpact run markpact-contracts/packs/desktop-automation-processes.markpact.md \
  --as flow --approve --dry-run

# lub --config z polem resolver_path:
urisys markpact run … --config edge.config.yaml
```

Przykład konwencji: `markpact-contracts/packs/examples/urisys.runtime.resolver.yaml`.  
Architektura: [`PROCESS-ARCHITECTURE.md`](PROCESS-ARCHITECTURE.md).

## Server

```bash
urisys --packs all serve --host 127.0.0.1 --port 8789
```

Endpointy:

```text
GET  /health
GET  /uri/routes
GET  /uri/events
POST /uri/call
POST /uri/explain
```

## Node (slave)

Minimalna instalacja na maszynie zdalnej (lenovo):

```bash
pip install urisys
urisys node serve --host 0.0.0.0 --port 8790
```

Packi **kvm/him/ocr/llm** i backendy **`[real]`** doinstalowują się przy pierwszym URI (domyślnie `URISYS_NODE_AUTO_INSTALL=1`). Wyłączenie:

```bash
urisys node serve --no-auto-install
```

Szczegóły: [`NODE-SETUP.md`](NODE-SETUP.md) · [`PACK-EXTENSIBILITY.md`](PACK-EXTENSIBILITY.md) · [`DISTRIBUTION.md`](DISTRIBUTION.md).

## Flow

```bash
urisys --packs all flow flows/device-maintenance.uri.flow.yaml --approve --dry-run
```

Format:

```yaml
flow:
  id: demo

defaults:
  approved: true
  dry_run: true
  environment: real

do:
  - systemd://unit/docker.service/query/status
  - docker://container/web/command/restart:
      reason: demo
```
