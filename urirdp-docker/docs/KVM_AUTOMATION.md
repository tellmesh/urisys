# KVM automation

Safe dry-run:

```bash
curl -X POST http://127.0.0.1:8795/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"kvm://local/task/command/click-text","payload":{"text":"OK"},"context":{"approved":true,"dry_run":true}}'
```

Real click in the RDP session:

```bash
URISYS_ALLOW_REAL=1 docker compose up --build urirdp
```

Then:

```bash
curl -X POST http://127.0.0.1:8795/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"him://local/mouse/command/click","payload":{"x":100,"y":100},"context":{"approved":true,"allow_real":true}}'
```

Keyboard typing:

```bash
curl -X POST http://127.0.0.1:8795/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"him://local/keyboard/command/type","payload":{"text":"Hello"},"context":{"approved":true,"allow_real":true}}'
```
