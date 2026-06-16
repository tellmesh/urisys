# Safety

KVM/HIM control can move the mouse and type on the host computer. The demo defaults to mock mode.

Real mode requires all of these:

```text
him.driver = pyautogui
context.approved = true
context.allow_real = true
```

or environment variable:

```bash
URISYS_ALLOW_REAL=1
```

Do not expose a real `him://` or `kvm://` server on a public network.
