# uricore-js

`uricore-js` is a small URI-native control core for browsers and Node.js.
It is not an agent framework. It is a deterministic layer:

```txt
URI -> manifest -> policy -> handler -> event -> result/projection
```

The same envelope can be used in a browser page, in a Node.js service, and across backends implemented in Python, Go, PHP, TypeScript, etc.

## Why

Traditional APIs often spread one operation across several representations:

- frontend function name,
- REST route,
- WebSocket event,
- backend handler,
- OpenAPI schema,
- queue event,
- audit log entry.

`uricore` makes the URI the shared semantic address:

```txt
page://state/counter/command/increment
node://counter/command/increment
py://math/add
printer://epson/command/nozzle-check
systemd://unit/nginx.service/command/restart
```

## Install / test

```bash
cd uricore-js
npm test
```

No build step is required. Browser examples import the source through native ES modules:

```html
<script type="module" src="./app.js"></script>
```

## Core API

```js
import {
  CapabilityRegistry,
  MemoryEventStore,
  PolicyGate,
  UriControlRuntime,
} from '@uricore/js';

const manifest = {
  id: 'counter-pack',
  version: 1,
  scheme: 'counter',
  uri_patterns: [
    {
      pattern: 'counter://main/command/increment',
      kind: 'command',
      operation: 'increment',
      handler: 'increment',
      side_effects: true,
      approval: 'required',
    },
  ],
};

let value = 0;
const registry = new CapabilityRegistry().loadManifest(manifest, {
  increment(payload) {
    value += Number(payload.step ?? 1);
    return { value };
  },
});

const runtime = new UriControlRuntime({
  registry,
  eventStore: new MemoryEventStore(),
  policy: new PolicyGate(),
});

const result = await runtime.call(
  'counter://main/command/increment',
  { step: 2 },
  { approved: true },
);
```

## Browser page demo

Run a Node server that serves the browser demo and exposes `/uri/call`:

```bash
node examples/node-server/server.mjs --static examples/browser-page --port 8080
```

Open:

```txt
http://127.0.0.1:8080/
```

The page has its own `uricore-js` runtime and can call:

```txt
page://state/counter/command/increment
page://dom/title/command/set
```

It can also call the Node service:

```txt
node://counter/command/increment
```

And it can call another browser tab/page through `BroadcastChannel`.

## Fullstack demo: browser + Node + Python

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

Flow:

```txt
browser page runtime
  page://state/counter/command/increment

browser -> Node HTTP
  node://counter/command/increment

browser -> Node HTTP -> Python HTTP
  node://python/math/add -> py://math/add
```

## Protocol adapters

The runtime has one internal contract:

```js
runtime.call(uri, payload, context)
```

Adapters expose that same contract through protocols:

| Protocol | Role | Files |
|---|---|---|
| HTTP | request/response calls | `src/server/http-server.js`, `src/transports/http-client.js` |
| SSE | server -> browser event stream | `src/server/http-server.js`, `src/transports/sse-client.js` |
| WebSocket | bidirectional calls and events | `src/server/ws-server.js`, `src/transports/ws-client.js` |
| BroadcastChannel | same-origin page/tab bridge | `src/transports/broadcast-channel.js` |
| postMessage | iframe/window bridge | `src/transports/post-message.js` |
| gRPC | service-to-service binary RPC skeleton | `src/server/grpc-adapter.js`, `contracts/proto/uricore/v1/envelope.proto` |

## Suggested split with Python uricore

```txt
uricore/       # Python core
uricore-js/    # browser + Node core
urisys/        # real system using both
```

`urisys` can import both runtimes and use the same envelope:

```json
{
  "uri": "py://math/add",
  "payload": { "a": 40, "b": 2 },
  "context": { "approved": true, "caller": "node-proxy" }
}
```

Response:

```json
{
  "ok": true,
  "uri": "py://math/add",
  "result": { "sum": 42, "backend": "python" },
  "event": { "event_type": "py.math.add.completed" }
}
```

## Framework integration examples

- React/Vue/Svelte/Angular: use `HttpUriClient` in a service/store/composable.
- Next.js/Nuxt/SvelteKit: route handler calls `runtime.call()`.
- Express/Fastify/Hono: adapt `POST /uri/call` to `runtime.call()`.
- FastAPI/Django/Flask: use the Python `uricore` runtime behind the same endpoint shape.
- NestJS: wrap `runtime.call()` in a provider/service and expose HTTP/WS gateways.
- Electron/Tauri: use `page://...` for UI runtime and `native://...` for desktop/backend runtime.

## Design rule

```txt
Pack knows technology.
Core knows URI, manifest, policy, dispatch and events.
Transport only carries envelopes.
```
