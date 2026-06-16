import { CapabilityRegistry, MemoryEventStore, PolicyGate, UriControlRuntime } from '../../src/index.js';
import { createHttpUriServer } from '../../src/server/http-server.js';
import { attachWebSocketUriServer } from '../../src/server/ws-server.js';
import { nodeManifest } from './manifest.js';

let counter = 0;

const handlers = {
  get_counter() {
    return { value: counter };
  },
  increment_counter(payload) {
    counter += Number(payload.step ?? 1);
    return { value: counter };
  },
  async python_math_add(payload) {
    const response = await fetch('http://127.0.0.1:8090/uri/call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uri: 'py://math/add',
        payload,
        context: { approved: true, caller: 'uricore-nodejs-proxy' },
      }),
    });
    if (!response.ok) {
      return { ok: false, note: 'Python backend is not running on :8090', payload };
    }
    return response.json();
  },
};

const registry = new CapabilityRegistry().loadManifest(nodeManifest, handlers);
const eventStore = new MemoryEventStore();
const runtime = new UriControlRuntime({
  registry,
  eventStore,
  policy: new PolicyGate({ requireApprovalForSideEffects: true }),
});

const args = new Set(process.argv.slice(2));
const portArgIndex = process.argv.findIndex((x) => x === '--port');
const port = portArgIndex >= 0 ? Number(process.argv[portArgIndex + 1]) : 8080;
const staticIndex = process.argv.findIndex((x) => x === '--static');
const staticDir = staticIndex >= 0 ? process.argv[staticIndex + 1] : 'examples/browser-page';

const server = createHttpUriServer({ runtime, staticDir });

try {
  await attachWebSocketUriServer(server, runtime);
  console.log('WebSocket URI endpoint enabled at /uri/ws');
} catch (error) {
  console.log('WebSocket endpoint skipped. Run `npm install` to install optional ws dependency.');
}

server.listen(port, () => {
  console.log(`uricore-js server listening on http://127.0.0.1:${port}`);
  console.log(`HTTP call: POST http://127.0.0.1:${port}/uri/call`);
  console.log(`SSE stream: http://127.0.0.1:${port}/uri/sse`);
  console.log(`Browser demo: http://127.0.0.1:${port}/`);
});
