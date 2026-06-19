export const DEVICE_ID = 'device-01';

export const API = Object.freeze({
  uriCall: '/api/uri/call',
  uris: '/api/uris',
});

export const URI = Object.freeze({
  eventsRecent: `mqtt://${DEVICE_ID}/events/query/recent`,
  ledSet: `mqtt://${DEVICE_ID}/led/command/set`,
  pingSend: `mqtt://${DEVICE_ID}/ping/command/send`,
  stateCurrent: `mqtt://${DEVICE_ID}/state/query/current`,
  telemetryLatest: `mqtt://${DEVICE_ID}/telemetry/query/latest`,
  topicsList: `mqtt://${DEVICE_ID}/topics/query/list`,
});

const URI_PATTERN = /^(?<scheme>[a-z][a-z0-9+.-]*):\/\/(?<target>[^/]+)\/(?<resource>[^/]+)\/(?<kind>command|query)\/(?<operation>[^/?#]+)$/i;

export function parseUri(uri) {
  const match = URI_PATTERN.exec(uri);
  if (!match) {
    throw new Error(`Invalid CQRS URI: ${uri}`);
  }
  return Object.freeze({ uri, ...match.groups });
}

function defineAction(name, uri) {
  const parsed = parseUri(uri);
  return Object.freeze({
    name,
    uri,
    scheme: parsed.scheme,
    target: parsed.target,
    resource: parsed.resource,
    kind: parsed.kind,
    operation: parsed.operation,
  });
}

export const CQRS = Object.freeze({
  command: Object.freeze({
    ledSet: defineAction('led.set', URI.ledSet),
    pingSend: defineAction('ping.send', URI.pingSend),
  }),
  query: Object.freeze({
    eventsRecent: defineAction('events.recent', URI.eventsRecent),
    stateCurrent: defineAction('state.current', URI.stateCurrent),
    telemetryLatest: defineAction('telemetry.latest', URI.telemetryLatest),
    topicsList: defineAction('topics.list', URI.topicsList),
  }),
});

function normalizeAction(actionOrUri) {
  if (typeof actionOrUri === 'string') {
    return defineAction(actionOrUri, actionOrUri);
  }
  if (!actionOrUri || typeof actionOrUri.uri !== 'string') {
    throw new Error('CQRS action must be an action object or URI string');
  }
  return actionOrUri;
}

function assertKind(action, expectedKind) {
  if (action.kind !== expectedKind) {
    throw new Error(`Expected ${expectedKind} URI, got ${action.kind}: ${action.uri}`);
  }
}

export function uriCall(actionOrUri, payload = {}, context = {}) {
  const action = normalizeAction(actionOrUri);
  return {
    uri: action.uri,
    payload,
    context: {
      ...context,
      cqrs: {
        kind: action.kind,
        name: action.name,
        operation: action.operation,
        resource: action.resource,
        target: action.target,
      },
    },
  };
}

export function command(actionOrUri, payload = {}, context = {}) {
  const action = normalizeAction(actionOrUri);
  assertKind(action, 'command');
  return uriCall(action, payload, context);
}

export function query(actionOrUri, payload = {}, context = {}) {
  const action = normalizeAction(actionOrUri);
  assertKind(action, 'query');
  return uriCall(action, payload, context);
}

export const Command = Object.freeze({
  setLed(on) {
    return command(CQRS.command.ledSet, { on: Boolean(on) });
  },
  ping(source = 'frontend') {
    return command(CQRS.command.pingSend, { source });
  },
});

export const Query = Object.freeze({
  eventsRecent() {
    return query(CQRS.query.eventsRecent);
  },
  stateCurrent() {
    return query(CQRS.query.stateCurrent);
  },
  telemetryLatest() {
    return query(CQRS.query.telemetryLatest);
  },
  topicsList() {
    return query(CQRS.query.topicsList);
  },
});

export const Contract = Object.freeze({
  API,
  CQRS,
  Command,
  DEVICE_ID,
  Query,
  URI,
});
