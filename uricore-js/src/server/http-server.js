import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import { extname, join, normalize, resolve } from 'node:path';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
};

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8') || '{}';
  return JSON.parse(raw);
}

function sendJson(res, status, data, cors) {
  if (cors) setCors(res);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data, null, 2));
}

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization');
}

export function createHttpUriServer({ runtime, staticDir = null, cors = true } = {}) {
  if (!runtime) throw new Error('createHttpUriServer requires runtime.');
  const sseClients = new Set();

  runtime.eventStore.subscribe?.((event) => {
    const payload = `event: uricore.event\ndata: ${JSON.stringify(event)}\n\n`;
    for (const res of sseClients) res.write(payload);
  });

  const server = http.createServer(async (req, res) => {
    try {
      if (cors) setCors(res);
      if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
      }

      const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

      if (req.method === 'GET' && url.pathname === '/health') {
        sendJson(res, 200, { ok: true, service: 'uricore-js' }, cors);
        return;
      }

      if (req.method === 'GET' && url.pathname === '/uri/capabilities') {
        sendJson(res, 200, { ok: true, capabilities: runtime.registry.listCapabilities() }, cors);
        return;
      }

      if (req.method === 'GET' && url.pathname === '/uri/events') {
        const since = Number(url.searchParams.get('since') || 0);
        const limit = Number(url.searchParams.get('limit') || 100);
        sendJson(res, 200, { ok: true, events: runtime.eventStore.list({ since, limit }) }, cors);
        return;
      }

      if (req.method === 'GET' && url.pathname === '/uri/sse') {
        res.writeHead(200, {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          Connection: 'keep-alive',
          'Access-Control-Allow-Origin': '*',
        });
        res.write(`event: uricore.ready\ndata: ${JSON.stringify({ ok: true })}\n\n`);
        sseClients.add(res);
        req.on('close', () => sseClients.delete(res));
        return;
      }

      if (req.method === 'POST' && (url.pathname === '/uri/call' || url.pathname === '/uri/query')) {
        const body = await readJson(req);
        const result = await runtime.call(body.uri, body.payload || {}, body.context || {});
        sendJson(res, result.ok ? 200 : 400, result, cors);
        return;
      }

      if (staticDir && req.method === 'GET') {
        const served = await tryServeStatic(staticDir, url.pathname, res);
        if (served) return;
      }

      sendJson(res, 404, { ok: false, error: 'not_found', path: url.pathname }, cors);
    } catch (error) {
      sendJson(res, 500, { ok: false, error: error.message }, cors);
    }
  });

  return server;
}

async function tryServeStatic(staticDir, pathname, res) {
  const root = resolve(staticDir);
  const requested = pathname === '/' ? '/index.html' : pathname;
  const file = normalize(join(root, decodeURIComponent(requested)));
  if (!file.startsWith(root)) return false;
  try {
    const info = await stat(file);
    if (!info.isFile()) return false;
    res.writeHead(200, { 'Content-Type': MIME[extname(file)] || 'application/octet-stream' });
    createReadStream(file).pipe(res);
    return true;
  } catch {
    return false;
  }
}
