export class HttpUriClient {
  constructor(baseUrl, { fetchImpl = globalThis.fetch } = {}) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.fetch = fetchImpl;
    if (!this.fetch) throw new Error('fetch is not available in this environment.');
  }

  async call(uri, payload = {}, context = {}) {
    const response = await this.fetch(`${this.baseUrl}/uri/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uri, payload, context }),
    });
    return response.json();
  }

  async query(uri, payload = {}, context = {}) {
    const response = await this.fetch(`${this.baseUrl}/uri/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uri, payload, context }),
    });
    return response.json();
  }

  async capabilities() {
    const response = await this.fetch(`${this.baseUrl}/uri/capabilities`);
    return response.json();
  }

  async events({ since = 0, limit = 100 } = {}) {
    const url = new URL(`${this.baseUrl}/uri/events`);
    url.searchParams.set('since', String(since));
    url.searchParams.set('limit', String(limit));
    const response = await this.fetch(url);
    return response.json();
  }
}
