export class WsUriClient {
  constructor(url, { WebSocketImpl = globalThis.WebSocket } = {}) {
    this.url = url;
    this.WebSocketImpl = WebSocketImpl;
    this.socket = null;
    this.pending = new Map();
    this.listeners = new Set();
  }

  connect() {
    if (!this.WebSocketImpl) throw new Error('WebSocket is not available in this environment.');
    this.socket = new this.WebSocketImpl(this.url);
    this.socket.addEventListener('message', (event) => this.#onMessage(event));
    return new Promise((resolve, reject) => {
      this.socket.addEventListener('open', () => resolve(this), { once: true });
      this.socket.addEventListener('error', reject, { once: true });
    });
  }

  call(uri, payload = {}, context = {}) {
    return this.#request('call', { uri, payload, context });
  }

  query(uri, payload = {}, context = {}) {
    return this.#request('query', { uri, payload, context });
  }

  onEvent(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  close() {
    this.socket?.close();
  }

  #request(type, body) {
    const id = `req_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const message = { id, type, ...body };
    this.socket.send(JSON.stringify(message));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`WebSocket URI request timed out: ${id}`));
        }
      }, 30000);
    });
  }

  #onMessage(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'event') {
      for (const listener of this.listeners) listener(data.event);
      return;
    }
    if (data.id && this.pending.has(data.id)) {
      const pending = this.pending.get(data.id);
      this.pending.delete(data.id);
      pending.resolve(data.result ?? data);
    }
  }
}
