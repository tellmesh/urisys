# uriscreen contract v0.1

Scheme: `screen://`

Routes:

```txt
screen://{node}/monitor/{monitor}/query/frame
screen://{node}/monitor/{monitor}/command/capture
screen://{node}/capture/command/loop
```

Backends: `mss`, `mock` (MVP).

Side effects require `approved: true` and `allow_real` for mss capture.
