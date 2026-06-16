# uriandroid

Separate Python URI capability pack for `android://`.

This package contains only:

- `manifest.yaml` — route/capability declaration
- `handlers.py` — implementation for the declared operations
- `common.py` — small safe/mock helper utilities

It does **not** contain a server, CLI, dashboard or hypervisor. Use `urisys` for controllers/managers:

```bash
urisys explain android://demo/query/status --packs android
urisys call android://demo/query/status --packs android
```

Real side effects are blocked by default. Use `--approve` for approved commands and `--allow-real` only when you intentionally want real OS/device actions.
