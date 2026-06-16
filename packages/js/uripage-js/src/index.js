export const manifest = {
  id: 'uripage-js',
  version: 1,
  scheme: 'page',
  description: 'Single-page state, navigation and event pack.',
  uri_patterns: [
    { pattern: 'page://state/{key}/query/get', kind: 'query', operation: 'getState', side_effects: false, approval: 'not_required' },
    { pattern: 'page://state/{key}/command/set', kind: 'command', operation: 'setState', side_effects: true, approval: 'not_required' },
    { pattern: 'page://route/command/push', kind: 'command', operation: 'pushRoute', side_effects: true, approval: 'not_required' },
    { pattern: 'page://event/{name}/command/emit', kind: 'command', operation: 'emitPageEvent', side_effects: true, approval: 'not_required' }
  ]
};

const state = new Map();

export const handlers = {
  getState(payload, context) {
    const key = context.params.key;
    return { key, value: state.get(key) ?? null };
  },
  setState(payload, context) {
    const key = context.params.key;
    const value = payload.value ?? payload;
    state.set(key, value);
    window.dispatchEvent(new CustomEvent('urisys:state', { detail: { key, value } }));
    return { key, value };
  },
  pushRoute(payload, context) {
    const path = String(payload.path || payload.url || '/');
    history.pushState(payload.state || {}, '', path);
    return { path, href: location.href };
  },
  emitPageEvent(payload, context) {
    const name = context.params.name;
    window.dispatchEvent(new CustomEvent(name, { detail: payload }));
    return { name, emitted: true };
  }
};

export function register(registry) {
  registry.loadManifest(manifest, handlers);
  return registry;
}
