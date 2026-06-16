# urikvm architecture

`kvm://` is a high-level computer-control contract. It should not directly know whether control is implemented by PyAutoGUI, VNC, RDP, a USB HID gadget, a browser automation bridge, or a physical KVM.

Layers:

```text
kvm:// task/display/monitor
  uses ocr:// to read screen text
  uses llm:// to decide action from screen/goal
  uses him:// to perform mouse/keyboard input
```

`him://` means Human Input Module in this example. It owns low-level keyboard and mouse actions.

Recommended boundary:

- `kvm://` — high-level task: screenshot, click text, type text, inspect monitor.
- `him://` — mouse and keyboard commands.
- `ocr://` — text extraction from screenshots.
- `llm://` — reasoning/vision analysis over OCR/screenshot.

Real control is disabled by default. Use mock for Docker and tests. Enable real input only on a trusted local machine with explicit `--allow-real`.
