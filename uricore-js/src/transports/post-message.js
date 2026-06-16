export class PostMessageBridge {
  constructor(targetWindow, targetOrigin = '*') {
    this.targetWindow = targetWindow;
    this.targetOrigin = targetOrigin;
    this.pending = new Map();
    globalThis.addEventListener?.('message', (event) => this.#onMessage(event));
  }

  attachRuntime(runtime) {
    globalThis.addEventListener?.('message', async (event) => {
      const msg = event.data;
      if (!msg || msg.protocol !== 'uricore' || msg.type !== 'call') return;
      const result = await runtime.call(msg.uri, msg.payload || {}, msg.context || {});
      event.source?.postMessage({ protocol: 'uricore', type: 'result', id: msg.id, result }, event.origin || '*');
    });
  }

  call(uri, payload = {}, context = {}) {
    const id = `pm_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    this.targetWindow.postMessage({ protocol: 'uricore', type: 'call', id, uri, payload, context }, this.targetOrigin);
    return new Promise((resolve) => {
      this.pending.set(id, resolve);
    });
  }

  #onMessage(event) {
    const msg = event.data;
    if (msg?.protocol === 'uricore' && msg.type === 'result' && this.pending.has(msg.id)) {
      const resolve = this.pending.get(msg.id);
      this.pending.delete(msg.id);
      resolve(msg.result);
    }
  }
}
