import { parseUri } from './parser.js';
import { HandlerNotFoundError, RouteNotFoundError } from './errors.js';

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function templateToRegex(pattern) {
  const names = [];
  const escaped = pattern
    .split(/(\{[^}]+\})/g)
    .map((part) => {
      if (part.startsWith('{') && part.endsWith('}')) {
        const name = part.slice(1, -1).trim();
        names.push(name);
        return `(?<${name}>[^/?#]+)`;
      }
      return escapeRegex(part);
    })
    .join('');
  return { regex: new RegExp(`^${escaped}$`), names };
}

export class CapabilityRegistry {
  constructor() {
    this.routes = [];
    this.handlers = new Map();
    this.manifests = [];
  }

  loadManifest(manifest, handlers = {}) {
    if (!manifest || !Array.isArray(manifest.uri_patterns)) {
      throw new Error('Manifest must contain uri_patterns array.');
    }
    this.manifests.push(manifest);

    for (const [name, fn] of Object.entries(handlers)) {
      this.handlers.set(name, fn);
    }

    for (const item of manifest.uri_patterns) {
      const route = this.#buildRoute(manifest, item, handlers);
      this.routes.push(route);
    }

    return this;
  }

  registerHandler(name, handler) {
    this.handlers.set(name, handler);
    return this;
  }

  listCapabilities() {
    return this.manifests.map((manifest) => ({
      id: manifest.id,
      version: manifest.version,
      scheme: manifest.scheme,
      description: manifest.description || '',
      uri_patterns: manifest.uri_patterns.map((r) => ({
        pattern: r.pattern,
        kind: r.kind,
        operation: r.operation,
        side_effects: Boolean(r.side_effects),
        approval: r.approval || 'not_required',
      })),
    }));
  }

  match(uri) {
    const parsed = parseUri(uri);
    for (const route of this.routes) {
      const match = route.regex.exec(uri);
      if (match) {
        return {
          ...route,
          uri,
          parsed,
          params: match.groups || {},
        };
      }
    }
    throw new RouteNotFoundError(`No capability route matched URI: ${uri}`, { uri });
  }

  #buildRoute(manifest, item, localHandlers) {
    if (!item.pattern || !item.operation) {
      throw new Error('Each uri_patterns entry must contain pattern and operation.');
    }
    const { regex, names } = templateToRegex(item.pattern);
    const handlerName = item.handler || item.operation;
    const handler = localHandlers[handlerName] || this.handlers.get(handlerName);

    return {
      manifest_id: manifest.id,
      scheme: manifest.scheme,
      pattern: item.pattern,
      regex,
      param_names: names,
      kind: item.kind || 'command',
      operation: item.operation,
      handler_name: handlerName,
      handler,
      command_type: item.command_type || null,
      query_type: item.query_type || null,
      result_type: item.result_type || null,
      success_event_type: item.success_event_type || `${manifest.id}.${item.operation}.completed`,
      failure_event_type: item.failure_event_type || `${manifest.id}.${item.operation}.failed`,
      side_effects: Boolean(item.side_effects),
      approval: item.approval || 'not_required',
      policy: { ...(manifest.policy || {}), ...(item.policy || {}) },
    };
  }
}

export function requireHandler(route) {
  if (typeof route.handler !== 'function') {
    throw new HandlerNotFoundError(`Handler not found for operation: ${route.operation}`, {
      operation: route.operation,
      handler_name: route.handler_name,
    });
  }
  return route.handler;
}
