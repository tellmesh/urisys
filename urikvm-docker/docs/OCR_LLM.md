# OCR and LLM drivers

## OCR (`ocr://`)

| Driver | Description |
|--------|-------------|
| `mock` | Fixed boxes from profile (`mock_boxes`) |
| `tesseract` | Real OCR from `state.latest_screenshot` PNG |

Tesseract requires:

```bash
sudo apt install tesseract-ocr   # system package
pip install -e ".[real]"         # pytesseract + Pillow
```

The screenshot must come from `kvm://.../screenshot` with `kvm.driver=mss` (or any handler that stores PNG in `latest_screenshot`).

## LLM vision (`llm://`)

| Driver | Description |
|--------|-------------|
| `mock` / `heuristic` | Match OCR boxes to goal text (no API) |
| `openai` | OpenAI vision model (`OPENAI_API_KEY`, default `gpt-4o-mini`) |
| `litellm` | Any LiteLLM vision model (`llm.model`, e.g. `openai/gpt-4o-mini`) |

When API key or network is missing, `openai` / `litellm` fall back to heuristic matching on OCR boxes.

**Important:** `mss` captures physical monitors; `pyautogui` under `xvfb-run` clicks a virtual display. For real desktop automation, run both on the same display (no xvfb). Use `scripts/real_pipeline.py --synthetic` to test OCR+LLM+HIM without a visible target on screen.

## Real profile example

`config/kvm-profile.real.json`:

```json
{
  "kvm": {"driver": "mss"},
  "him": {"driver": "pyautogui"},
  "ocr": {"driver": "tesseract", "lang": "eng"},
  "llm": {"driver": "openai", "model": "gpt-4o-mini"}
}
```

## End-to-end flow

```text
kvm://local/task/command/click-text
  → kvm://.../screenshot        (mss PNG → state)
  → ocr://.../text              (tesseract boxes)
  → llm://.../analyze           (openai vision or heuristic)
  → him://.../mouse/click       (pyautogui)
```
