# Shared Python packages (urisys monorepo)

## `urisysedge`

Canonical **edge runtime** for Docker-based URI servers.

| Module | Exports |
|--------|---------|
| `runtime.py` | `Route`, `Runtime`, `JsonlEventStore`, `load_json`, `run_flow`, HTTP `serve` |
| `env.py` | `load_env_policy`, `resolve_env_var`, `load_urisys_env` |

### Consumers (shims)

- `urirdp-docker/packages/python/urirdpedge/`
- `urisys-automation-lab/packages/python/labedge/`
- `urikvm-docker/packages/python/urikvmedge/`
- `uribrowser-docker/packages/python/uribrowseredge/`
- `urisys-node/packages/python/urisysnode/` (`runtime.py`, `env.py`)

### Local dev

```bash
export PYTHONPATH="/path/to/urisys/packages/python:/path/to/tellmesh/urirdp-docker/packages/python"
python3 -c "from urisysedge.runtime import Runtime; r=Runtime(); print(r)"
```

### Docker

Both `urirdp-docker/Dockerfile` and `urisys-automation-lab/Dockerfile` copy:

```dockerfile
COPY packages/python/urisysedge ./packages/python/urisysedge
```

Build context must be the **`urisys/`** repository root.

See [`docs/PACKAGES.md`](../docs/PACKAGES.md) for the full duplicate catalog.
