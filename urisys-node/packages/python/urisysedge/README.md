# urisysedge (vendored path)

Canonical implementation: [`../../../packages/python/urisysedge/`](../../../packages/python/urisysedge/).

In the **urisys monorepo**, `packages/python/urisysedge` is the single source (see root `pyproject.toml`).

For **standalone `urisys-node` wheel** builds, populate this directory before sdist:

```bash
bash scripts/sync-vendored-urisysedge.sh
```

Do not edit `runtime.py` / `env.py` here — change the canonical copy and re-sync.
