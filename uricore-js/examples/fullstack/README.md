# uricore-js fullstack demo

This example shows three runtimes using the same envelope:

```txt
browser uricore-js
  page://state/counter/command/increment
        │
        ├─ HTTP POST /uri/call
        ▼
Node uricore-js server
  node://counter/command/increment
  node://python/math/add
        │
        ├─ HTTP POST /uri/call
        ▼
Python uricore-compatible backend
  py://math/add
```

## Run

Terminal 1:

```bash
python examples/python-backend/server.py
```

Terminal 2:

```bash
node examples/node-server/server.mjs --static examples/browser-page --port 8080
```

Open:

```txt
http://127.0.0.1:8080/
```

## Protocols in the demo

- Local browser runtime: direct in-memory `runtime.call(uri, payload)`.
- Browser → Node: HTTP `POST /uri/call`.
- Node → Browser events: SSE `GET /uri/sse`.
- Browser tab → Browser tab: `BroadcastChannel`.
- Browser ↔ Node WebSocket: optional `/uri/ws` when `ws` is installed.
- Node gRPC: optional adapter in `src/server/grpc-adapter.js`.
