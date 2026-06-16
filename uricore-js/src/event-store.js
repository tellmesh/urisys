export function nowIso() {
  return new Date().toISOString();
}

export function newId(prefix = 'evt') {
  const rand = Math.random().toString(36).slice(2, 10);
  return `${prefix}_${Date.now().toString(36)}_${rand}`;
}

export class MemoryEventStore {
  constructor() {
    this.events = [];
    this.listeners = new Set();
  }

  append(event) {
    const normalized = {
      event_id: event.event_id || newId('evt'),
      occurred_at: event.occurred_at || nowIso(),
      ...event,
    };
    this.events.push(normalized);
    for (const listener of this.listeners) {
      try {
        listener(normalized);
      } catch {
        // listener errors must not break command processing
      }
    }
    return normalized;
  }

  list({ since = 0, limit = 100 } = {}) {
    return this.events.slice(since, since + limit);
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

export class LocalStorageEventStore extends MemoryEventStore {
  constructor(key = 'uricore.events') {
    super();
    this.key = key;
    if (typeof localStorage !== 'undefined') {
      try {
        this.events = JSON.parse(localStorage.getItem(this.key) || '[]');
      } catch {
        this.events = [];
      }
    }
  }

  append(event) {
    const normalized = super.append(event);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.key, JSON.stringify(this.events));
    }
    return normalized;
  }

  clear() {
    this.events = [];
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(this.key);
    }
  }
}
