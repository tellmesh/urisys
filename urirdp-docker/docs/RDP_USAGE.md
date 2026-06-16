# RDP usage

1. Start container:

```bash
docker compose up --build urirdp
```

2. Connect with any RDP client:

```text
Host: 127.0.0.1
Port: 3389
User: urisys
Password: urisys
```

3. Check the URI server:

```bash
curl http://127.0.0.1:8795/health
curl http://127.0.0.1:8795/uri/routes
```

4. Detect the active X display:

```bash
curl -X POST http://127.0.0.1:8795/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"rdp://local/session/query/display"}'
```

If real automation fails with `Cannot open display`, connect through RDP first, then retry. You can also pass the display explicitly:

```json
{"context":{"display":":10","approved":true,"allow_real":true}}
```
