export class SseUriClient {
  constructor(url, { EventSourceImpl = globalThis.EventSource } = {}) {
    this.url = url;
    this.EventSourceImpl = EventSourceImpl;
    this.source = null;
  }

  connect({ onEvent, onOpen, onError } = {}) {
    if (!this.EventSourceImpl) throw new Error('EventSource is not available in this environment.');
    this.source = new this.EventSourceImpl(this.url);
    this.source.addEventListener('open', (event) => onOpen?.(event));
    this.source.addEventListener('error', (event) => onError?.(event));
    this.source.addEventListener('message', (event) => {
      try {
        onEvent?.(JSON.parse(event.data));
      } catch {
        onEvent?.(event.data);
      }
    });
    this.source.addEventListener('uricore.event', (event) => {
      try {
        onEvent?.(JSON.parse(event.data));
      } catch {
        onEvent?.(event.data);
      }
    });
    return this;
  }

  close() {
    this.source?.close();
    this.source = null;
  }
}
