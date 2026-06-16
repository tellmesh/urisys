import { CapabilityRegistry, LocalStorageEventStore, PolicyGate, UriControlRuntime } from '../../src/index.js';
import { BroadcastChannelBridge } from '../../src/transports/broadcast-channel.js';
import { pageManifest } from './manifest.js';

const state = { counter: Number(localStorage.getItem('peer_counter') || 0) };
const $ = (id) => document.getElementById(id);
function render() { $('counter').textContent = String(state.counter); }

const handlers = {
  get_state(_payload, context) {
    return { key: context.params.key, value: state[context.params.key] ?? null };
  },
  set_state(payload, context) {
    state[context.params.key] = payload.value;
    localStorage.setItem('peer_counter', String(payload.value));
    render();
    return { key: context.params.key, value: payload.value };
  },
  increment_state(payload, context) {
    const key = context.params.key;
    state[key] = Number(state[key] || 0) + Number(payload.step ?? 1);
    localStorage.setItem('peer_counter', String(state[key]));
    render();
    return { key, value: state[key], page: 'peer' };
  },
  set_title(payload) {
    document.title = payload.title;
    return { title: payload.title };
  },
};

const runtime = new UriControlRuntime({
  registry: new CapabilityRegistry().loadManifest(pageManifest, handlers),
  eventStore: new LocalStorageEventStore('uricore.peer.events'),
  policy: new PolicyGate({ requireApprovalForSideEffects: false }),
});
new BroadcastChannelBridge('uricore.demo.pagebus').attachRuntime(runtime);
render();
