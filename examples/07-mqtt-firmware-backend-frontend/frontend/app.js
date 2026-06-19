const state = {
  topics: {},
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

function ms(value) {
  if (typeof value !== 'number') return '-';
  return `${Math.round(value / 1000)}s`;
}

function render(data) {
  const device = data.state || {};
  const telemetry = data.telemetry || {};
  const online = device.online === true;

  $('#online-dot').classList.toggle('online', online);
  $('#online-text').textContent = online ? 'online' : 'waiting';
  $('#device-id').textContent = device.device_id || telemetry.device_id || '-';
  $('#led-state').textContent = device.led === true ? 'on' : device.led === false ? 'off' : '-';
  $('#uptime').textContent = ms(telemetry.uptime_ms || device.uptime_ms);
  $('#temperature').textContent = typeof telemetry.temperature_c === 'number' ? `${telemetry.temperature_c} C` : '-';
  $('#topics').textContent = JSON.stringify(data.topics || state.topics, null, 2);
  $('#events').textContent = JSON.stringify(data.events || [], null, 2);
}

async function refresh() {
  const data = await api('/api/device/state');
  state.topics = data.topics || state.topics;
  render(data);
}

async function setLed(on) {
  await api('/api/device/led', {
    method: 'POST',
    body: JSON.stringify({ on }),
  });
  setTimeout(refresh, 150);
}

async function ping() {
  await api('/api/device/ping', {
    method: 'POST',
    body: JSON.stringify({ source: 'frontend' }),
  });
  setTimeout(refresh, 150);
}

$('#led-on').addEventListener('click', () => setLed(true).catch(console.error));
$('#led-off').addEventListener('click', () => setLed(false).catch(console.error));
$('#ping').addEventListener('click', () => ping().catch(console.error));

refresh().catch(console.error);
setInterval(() => refresh().catch(console.error), 1000);
