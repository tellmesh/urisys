# RDP real integration test (e2e)

Separate from fast mock smoke (`scripts/test-docker.sh`).

## Layout

```text
docker-compose.rdp-e2e.yml
  urirdp          xrdp :3389, URI :8795, URISYS_ALLOW_REAL=1
  rdp-client      Xvfb :99 + xfreerdp → urirdp:3389

tests/e2e_rdp_real.sh
scripts/test-rdp-real.sh
make test-rdp-real
```

## Flow

```text
rdp-client
  Xvfb :99
  xfreerdp → urirdp:3389
  wait rdp://local/display/query/status (display_exists + xdpyinfo_ok)
  rdp://local/session/command/prepare-target (zenity OK)
  kvm://local/task/command/click-text (allow_real)
    → scrot → tesseract → mock-vision → xdotool
```

## Run locally

```bash
make test-rdp-real
```

## CI

GitHub Actions job `urirdp-rdp-real` — `workflow_dispatch` or PR touching `urirdp-docker/**`.

Not wired into default smoke; run manually or in the dedicated workflow.

## Status URI

`rdp://local/display/query/status` returns:

```json
{
  "display": ":10",
  "display_exists": true,
  "xdpyinfo_ok": true,
  "screenshot_ok": true,
  "ready": true
}
```

## KVM result shape

`kvm://local/task/command/click-text` includes:

```json
{
  "clicked": true,
  "pipeline": {
    "screenshot": {"ok": true},
    "ocr": {"ok": true},
    "llm": {"ok": true},
    "him": {"ok": true, "result": {"driver": "xdotool"}}
  }
}
```
