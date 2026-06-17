import { CapabilityRegistry, UriControlRuntime, MemoryEventStore } from '../../../uricore-js/src/index.js';
import { register as registerDom } from '../../../uri-packs/packages/js/uridom-js/src/index.js';
import { register as registerPage } from '../../../uri-packs/packages/js/uripage-js/src/index.js';
import { HttpUriClient } from '../../../uricore-js/src/transports/http-client.js';

const registry = new CapabilityRegistry();
registerDom(registry);
registerPage(registry);
const runtime = new UriControlRuntime({ registry, eventStore: new MemoryEventStore() });
const out = document.querySelector('#out');

document.querySelector('#local').addEventListener('click', async () => {
  const result = await runtime.call('dom://element/%23status/command/set-text', { text: 'Zmienione lokalnie przez dom:// URI' });
  out.textContent = JSON.stringify(result, null, 2);
});

document.querySelector('#node').addEventListener('click', async () => {
  const client = new HttpUriClient('http://127.0.0.1:8789');
  const result = await client.call('llm://mock/chat/query/completion', { messages: [{ role: 'user', content: 'Hello from browser' }] }, { approved: true, environment: 'mock' });
  out.textContent = JSON.stringify(result, null, 2);
});
