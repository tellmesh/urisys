# urisys-node contract v0.1

Installable slave service exposing:

```txt
GET  /health
GET  /uri/routes
GET  /events
POST /uri/call
```

Identity:

```txt
node_id, fingerprint, public_key, paired, capabilities
```

Pairing required before mutating operations (unless URISYS_NODE_SKIP_PAIRING=1 dev).

Transport is separate from URI command namespace.
