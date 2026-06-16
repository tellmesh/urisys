# uriwebrtc contract (MVP)

Scheme: `webrtc://`

## Routes

```txt
webrtc://local/session/{session}/command/start
webrtc://local/session/{session}/data/command/send
```

## Role

Transport only — media + DataChannel URI envelopes.

Execution stays in `kvm://`, `him://`, `rdp://`, etc.

## DataChannel envelope

```json
{
  "uri": "kvm://local/task/command/click-text",
  "payload": { "text": "OK" },
  "context": { "approved": true, "dry_run": true }
}
```

Signaling (future): `signaling://local/room/{id}/…`
