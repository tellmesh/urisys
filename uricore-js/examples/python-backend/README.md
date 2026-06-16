# Python backend example

Run:

```bash
python examples/python-backend/server.py
```

It exposes the same envelope as uricore-js:

```bash
curl -X POST http://127.0.0.1:8090/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"py://math/add","payload":{"a":40,"b":2},"context":{"approved":true}}'
```

The Node example proxies `node://python/math/add` to this Python URI.
