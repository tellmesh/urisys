# uribrowser

Separate Python URI capability pack for `browser://`.

This package contains only:

- `manifest.yaml` — route/capability declaration
- `handlers.py` — implementation for the declared operations
- `common.py` — small safe/mock helper utilities

It does **not** contain a server, CLI, dashboard or hypervisor. Use `urisys` for controllers/managers:

```bash
urisys explain browser://demo/query/status --packs browser
urisys call browser://demo/query/status --packs browser
```

Real side effects are blocked by default. Use `--approve` for approved commands and `--allow-real` only when you intentionally want real OS/device actions.
