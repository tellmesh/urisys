# Architecture

```text
RDP client
  -> XRDP session in container
  -> XFCE desktop
  -> X11 display, usually :10

URI client
  -> POST /uri/call on port 8795
  -> urisys-rdp runtime
  -> rdp://, kvm://, him://, ocr://, llm:// handlers
  -> X11 tools: xdotool, scrot, tesseract
```

`URL` is only the transport address. `URI` is the command/resource identity.

Example:

```text
POST http://127.0.0.1:8795/uri/call
{
  "uri": "kvm://local/task/command/click-text",
  "payload": {"text": "OK"},
  "context": {"approved": true}
}
```

The task-level route calls lower layers:

```text
kvm://.../screenshot
ocr://.../text
llm://.../analyze
him://.../click
```
