import {
  CapabilityRegistry,
  LocalStorageEventStore,
  PolicyGate,
  UriControlRuntime,
} from '../../src/index.js';
import { HttpUriClient } from '../../src/transports/http-client.js';
import { SseUriClient } from '../../src/transports/sse-client.js';
import { BroadcastChannelBridge } from '../../src/transports/broadcast-channel.js';
import { pageManifest } from './manifest.js';

const state = { counter: Number(localStorage.getItem('counter') || 0) };
const $ = (id) => document.getElementById(id);

function render() {
  $('counter').textContent = String(state.counter);
  $('events').textContent = runtime.eventStore.list({ limit: 200 }).map((e) => JSON.stringify(e)).join('\n');
}

const handlers = {
  get_state(_payload, context) {
    return { key: context.params.key, value: state[context.params.key] ?? null };
  },
  set_state(payload, context) {
    state[context.params.key] = payload.value;
    localStorage.setItem(context.params.key, String(payload.value));
    render();
    return { key: context.params.key, value: payload.value };
  },
  increment_state(payload, context) {
    const step = Number(payload.step ?? 1);
    const key = context.params.key;
    state[key] = Number(state[key] || 0) + step;
    localStorage.setItem(key, String(state[key]));
    render();
    return { key, value: state[key] };
  },
  set_title(payload) {
    document.title = payload.title;
    $('title').textContent = payload.title;
    return { title: payload.title };
  },
};

const registry = new CapabilityRegistry().loadManifest(pageManifest, handlers);
const runtime = new UriControlRuntime({
  registry,
  eventStore: new LocalStorageEventStore('uricore.demo.events'),
  policy: new PolicyGate({ requireApprovalForSideEffects: false }),
});
const nodeClient = new HttpUriClient(location.origin);
const sse = new SseUriClient(`${location.origin}/uri/sse`);
const bus = new BroadcastChannelBridge('uricore.demo.pagebus');
bus.attachRuntime(runtime);

$('local-inc').onclick = async () => {
  const result = await runtime.call('page://state/counter/command/increment', { step: 1 });
  $('last').textContent = JSON.stringify(result, null, 2);
  render();
};

$('set-title').onclick = async () => {
  const title = `URI page ${new Date().toLocaleTimeString()}`;
  const result = await runtime.call('page://dom/title/command/set', { title });
  $('last').textContent = JSON.stringify(result, null, 2);
  render();
};

$('node-inc').onclick = async () => {
  const result = await nodeClient.call('node://counter/command/increment', { step: 1 }, { approved: true });
  $('last').textContent = JSON.stringify(result, null, 2);
};

$('python-add').onclick = async () => {
  const result = await nodeClient.call('node://python/math/add', { a: 40, b: 2 }, { approved: true });
  $('last').textContent = JSON.stringify(result, null, 2);
};

$('peer-inc').onclick = async () => {
  const result = await bus.call('page://state/counter/command/increment', { step: 5 });
  $('last').textContent = JSON.stringify(result, null, 2);
};

sse.connect({
  onEvent(event) {
    $('remote-events').textContent = `${JSON.stringify(event)}\n${$('remote-events').textContent}`;
  },
});

render();
