# urillm

Separate Python URI capability pack for `llm://`.

This package contains only:

- `manifest.yaml` — route/capability declaration
- `handlers.py` — implementation for the declared operations
- `common.py` — small safe/mock helper utilities

It does **not** contain a server, CLI, dashboard or hypervisor. Use `urisys` for controllers/managers:

```bash
urisys explain llm://demo/query/status --packs llm
urisys call llm://demo/query/status --packs llm
```

Real side effects are blocked by default. Use `--approve` for approved commands and `--allow-real` only when you intentionally want real OS/device actions.
