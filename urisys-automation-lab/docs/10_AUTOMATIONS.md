# 10 automations

| # | Flow | Layer |
|---|------|-------|
| 01 | install browser | shell/TUI |
| 02 | update system | shell/TUI |
| 03 | open browser GUI | browser:// |
| 04 | browser download/raw | browser:// |
| 05 | fill form | OCR+KVM+HIM |
| 06 | htop TUI | shell+HIM |
| 07 | nano config | shell+HIM |
| 08 | voice → KVM | stt:// + chat:// |
| 09 | WebRTC + RDP | webrtc:// + chat:// |
| 10 | full maintenance | env+shell+browser+kvm+rdp |

Validate:

```bash
bash scripts/validate-flows.sh
```
