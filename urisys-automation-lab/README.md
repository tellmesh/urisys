# urisys-automation-lab

10 przykładowych automatyzacji (TUI + GUI + STT + WebRTC) z lokalnym interfejsem web.

## Szybki start

### Docker (zalecane — jeden stack)

```bash
cd urisys/urisys-automation-lab
bash scripts/docker-up.sh
bash scripts/docker-smoke.sh   # opcjonalnie
```

| Usługa | URL |
|--------|-----|
| Lab UI + STT/chat/WebRTC | http://127.0.0.1:8099 |
| urirdp URI API | http://127.0.0.1:8795/uri/call |
| RDP desktop | `127.0.0.1:3389` (user `urisys`) |

Zatrzymanie: `bash scripts/docker-down.sh` · logi: `bash scripts/docker-logs.sh`

### Lokalnie (bez Docker)

```bash
cd urisys/urisys-automation-lab
bash scripts/validate-flows.sh
bash scripts/run-lab.sh
```

## Stack

```txt
flows/*.uri.flow.yaml     → uri2flow
server/                   → lab gateway :8099
packages/python/          → uristt, urichat, uriwebrtc (mock MVP)
web/                      → getUserMedia + Web Speech + WebRTC DataChannel
urirdp-docker :8795       → rdp/kvm/him/ocr/llm execution
```

## Flow 08 (voice → KVM)

```yaml
do:
  - stt://local/session/main/command/start
  - stt://local/session/main/query/transcript
  - chat://local/uri/command/execute:
      uri: kvm://local/task/command/click-text
      payload: { text: OK }
```

## Powiązane

- [`tellmesh/examples/39_system_automations`](../../tellmesh/examples/39_system_automations/)
- [`urisys-node`](../urisys-node/) — jawnie zainstalowany slave runtime (:8790)
- [`uri2voice`](../../uri2voice/) — produkcyjny STT/TTS przez touri
- [`urirdp-docker`](../urirdp-docker/)

## Docs

- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [STT.md](docs/STT.md)
- [WEBRTC_CHAT.md](docs/WEBRTC_CHAT.md)
- [10_AUTOMATIONS.md](docs/10_AUTOMATIONS.md)
