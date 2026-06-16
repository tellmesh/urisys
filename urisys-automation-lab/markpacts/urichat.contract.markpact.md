# urichat contract (MVP)

Scheme: `chat://`

## Routes

```txt
chat://local/message/command/send
chat://local/uri/command/execute
```

## Role

Map natural language / transcript → URI envelope → forward to urisys (`/uri/call`).

Does **not** replace `llm://` planning — it is a thin bridge for voice/UI commands.

## Example

```json
{
  "uri": "chat://local/uri/command/execute",
  "payload": {
    "transcript": "kliknij OK",
    "approved": true,
    "dry_run": true
  }
}
```
