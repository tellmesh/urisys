import test from 'node:test';
import assert from 'node:assert/strict';
import { CapabilityRegistry, MemoryEventStore, PolicyGate, UriControlRuntime } from '../src/index.js';

const manifest = {
  id: 'test-pack',
  version: 1,
  scheme: 'test',
  uri_patterns: [
    {
      pattern: 'test://counter/command/inc',
      kind: 'command',
      operation: 'inc',
      handler: 'inc',
      side_effects: true,
      approval: 'required',
      success_event_type: 'test.counter.incremented',
    },
    {
      pattern: 'test://counter/query/get',
      kind: 'query',
      operation: 'get',
      handler: 'get',
      side_effects: false,
    },
  ],
};

test('runtime blocks side effects without approval', async () => {
  let counter = 0;
  const runtime = new UriControlRuntime({
    registry: new CapabilityRegistry().loadManifest(manifest, {
      inc(payload) { counter += payload.step ?? 1; return { counter }; },
      get() { return { counter }; },
    }),
    eventStore: new MemoryEventStore(),
    policy: new PolicyGate(),
  });

  const result = await runtime.call('test://counter/command/inc', { step: 2 });
  assert.equal(result.ok, false);
  assert.equal(result.error.type, 'policy_denied');
});

test('runtime executes approved command and writes events', async () => {
  let counter = 0;
  const store = new MemoryEventStore();
  const runtime = new UriControlRuntime({
    registry: new CapabilityRegistry().loadManifest(manifest, {
      inc(payload) { counter += payload.step ?? 1; return { counter }; },
      get() { return { counter }; },
    }),
    eventStore: store,
    policy: new PolicyGate(),
  });

  const result = await runtime.call('test://counter/command/inc', { step: 2 }, { approved: true });
  assert.equal(result.ok, true);
  assert.equal(result.result.counter, 2);
  assert.equal(store.list().length, 2);
});
