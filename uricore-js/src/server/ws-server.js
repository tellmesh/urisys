// Optional WebSocket server adapter. Requires: npm install ws
export async function attachWebSocketUriServer(httpServer, runtime) {
  const { WebSocketServer } = await import('ws');
  const wss = new WebSocketServer({ server: httpServer, path: '/uri/ws' });

  const unsubscribe = runtime.eventStore.subscribe?.((event) => {
    const msg = JSON.stringify({ type: 'event', event });
    for (const client of wss.clients) {
      if (client.readyState === 1) client.send(msg);
    }
  });

  wss.on('connection', (socket) => {
    socket.on('message', async (raw) => {
      const msg = JSON.parse(raw.toString());
      if (msg.type === 'call' || msg.type === 'query') {
        const result = await runtime.call(msg.uri, msg.payload || {}, msg.context || {});
        socket.send(JSON.stringify({ id: msg.id, type: 'result', result }));
      }
    });
  });

  wss.on('close', () => unsubscribe?.());
  return wss;
}
