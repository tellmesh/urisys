# urihim

`him://` URI capability pack (Human Input Machine — mouse/keyboard) for
[`urisys-node`](https://github.com/tellmesh/urisys).

Provides `him://{host}/mouse/...` and `him://{host}/keyboard/...` commands backed
by `pyautogui` (X11), `ydotool` (Wayland) or `xdotool`, with a mock driver when
no real backend is allowed.

```bash
pip install "urihim[real]"
```

Loaded into a node either at boot (`URISYS_NODE_PACKS=...,him`) or hot-loaded over
the wire (`POST /uri/pack {"pack":"him"}`). See the urisys docs for the full
capability model and approval policy.

Licensed under Apache-2.0.
