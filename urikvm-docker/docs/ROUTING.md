# Routing

Transport URL:

```text
POST http://workstation.local:8794/uri/call
```

Logical commands:

```text
kvm://local/task/command/click-text
him://local/mouse/command/click
ocr://local/image/latest/query/text
llm://local/vision/query/analyze
```

A remote controller can route `kvm://pc-01/**` to `http://pc-01.local:8794/uri/call`, while local handlers still execute `him://pc-01/**` on that machine.
