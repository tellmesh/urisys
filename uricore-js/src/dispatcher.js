import { requireHandler } from './registry.js';
import { MemoryEventStore, newId } from './event-store.js';
import { PolicyGate } from './policy.js';
import { HandlerExecutionError, PolicyDeniedError, UriCoreError } from './errors.js';

export class UriControlRuntime {
  constructor({ registry, eventStore = new MemoryEventStore(), policy = new PolicyGate() } = {}) {
    if (!registry) throw new Error('UriControlRuntime requires registry.');
    this.registry = registry;
    this.eventStore = eventStore;
    this.policy = policy;
  }

  async call(uri, payload = {}, context = {}) {
    const commandId = context.command_id || newId('cmd');
    let route;

    try {
      route = this.registry.match(uri);
      const policyDecision = this.policy.check(route, payload, context);

      this.eventStore.append({
        event_type: 'uricore.command.accepted',
        source_uri: uri,
        command_id: commandId,
        operation: route.operation,
        payload,
        policy: policyDecision,
      });

      const handler = requireHandler(route);
      const result = await handler(payload, {
        ...context,
        uri,
        params: route.params,
        parsed: route.parsed,
        operation: route.operation,
        command_id: commandId,
      });

      const event = this.eventStore.append({
        event_type: route.success_event_type,
        source_uri: uri,
        command_id: commandId,
        operation: route.operation,
        payload: result,
      });

      return {
        ok: true,
        uri,
        kind: route.kind,
        operation: route.operation,
        command_id: commandId,
        event,
        result,
      };
    } catch (error) {
      const normalized = this.#normalizeError(error);
      const event = this.eventStore.append({
        event_type: route?.failure_event_type || 'uricore.operation.failed',
        source_uri: uri,
        command_id: commandId,
        operation: route?.operation || null,
        error: normalized,
      });

      return {
        ok: false,
        uri,
        kind: route?.kind || null,
        operation: route?.operation || null,
        command_id: commandId,
        event,
        error: normalized,
      };
    }
  }

  async query(uri, payload = {}, context = {}) {
    return this.call(uri, payload, { ...context, approved: context.approved ?? false });
  }

  explain(uri) {
    const route = this.registry.match(uri);
    return {
      ok: true,
      uri,
      manifest_id: route.manifest_id,
      scheme: route.scheme,
      pattern: route.pattern,
      kind: route.kind,
      operation: route.operation,
      command_type: route.command_type,
      query_type: route.query_type,
      result_type: route.result_type,
      side_effects: route.side_effects,
      approval: route.approval,
      params: route.params,
    };
  }

  #normalizeError(error) {
    if (error instanceof PolicyDeniedError) {
      return { type: 'policy_denied', message: error.message, details: error.details || {} };
    }
    if (error instanceof UriCoreError) {
      return { type: error.name, message: error.message, details: error.details || {} };
    }
    if (error instanceof Error) {
      return { type: 'handler_error', message: error.message, details: {} };
    }
    return { type: 'unknown_error', message: String(error), details: {} };
  }
}
