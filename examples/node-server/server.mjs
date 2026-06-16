import { CapabilityRegistry, UriControlRuntime, MemoryEventStore } from '../../uricore-js/src/index.js';
import { createHttpUriServer } from '../../uricore-js/src/server/http-server.js';
import { register as registerNode } from '../../packages/js/urinode-js/src/index.js';

const registry = new CapabilityRegistry();
registerNode(registry);
const runtime = new UriControlRuntime({ registry, eventStore: new MemoryEventStore() });
const server = createHttpUriServer({ runtime, staticDir: new URL('../../urisys/examples/frontend', import.meta.url).pathname });
const port = Number(process.env.PORT || 8790);
server.listen(port, '127.0.0.1', () => {
  console.log(`urinode-js demo server on http://127.0.0.1:${port}`);
  console.log('POST /uri/call accepts node:// and node://bridge/command/call');
});
