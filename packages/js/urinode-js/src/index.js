import process from 'node:process';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

export const manifest = {
  id: 'urinode-js',
  version: 1,
  scheme: 'node',
  description: 'Node.js process/server control pack.',
  uri_patterns: [
    { pattern: 'node://process/query/info', kind: 'query', operation: 'processInfo', side_effects: false, approval: 'not_required' },
    { pattern: 'node://env/{name}/query/get', kind: 'query', operation: 'getEnv', side_effects: false, approval: 'not_required' },
    { pattern: 'node://shell/command/run', kind: 'command', operation: 'runShell', side_effects: true, approval: 'required' },
    { pattern: 'node://bridge/command/call', kind: 'command', operation: 'bridgeCall', side_effects: true, approval: 'not_required' }
  ]
};

async function postJson(url, body) {
  const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return response.json();
}

export const handlers = {
  processInfo() {
    return { pid: process.pid, platform: process.platform, node: process.version, cwd: process.cwd() };
  },
  getEnv(payload, context) {
    const name = context.params.name;
    return { name, value: process.env[name] ?? null };
  },
  async runShell(payload, context) {
    if (!context.allow_real) return { mode: 'mock', command: payload.command || [], executed: false };
    const command = Array.isArray(payload.command) ? payload.command : String(payload.command || '').split(/\s+/).filter(Boolean);
    if (!command.length) throw new Error('payload.command is required');
    const [bin, ...args] = command;
    const result = await execFileAsync(bin, args, { timeout: payload.timeout || 15000 });
    return { mode: 'real', command, stdout: result.stdout, stderr: result.stderr };
  },
  async bridgeCall(payload) {
    const endpoint = payload.endpoint || 'http://127.0.0.1:8789/uri/call';
    return postJson(endpoint, { uri: payload.uri, payload: payload.payload || {}, context: payload.context || {} });
  }
};

export function register(registry) {
  registry.loadManifest(manifest, handlers);
  return registry;
}
