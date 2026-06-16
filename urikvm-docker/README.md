# urikvm-docker

Portable computer-control example with:

- `kvm://` — high-level monitor/task control.
- `him://` — keyboard and mouse control.
- `ocr://` — screen text extraction.
- `llm://` — screen/action reasoning.

Docker runs in mock mode, so it does not control the host mouse or keyboard.

**PyPI:** `urikvm`, `urihim`, `uriocr`, `urillm` mają osobne `pyproject.toml` (gotowe do publikacji). Ten katalog instaluje meta-bundle `urikvm-docker-example` — **nie** zastępuje `pip install urikvm`. Z monorepo: `bash scripts/install-kvm-packs-editable.sh`.

```bash
python -m pip install -e .
urisys-kvm call kvm://local/task/command/click-text \
  --payload '{"text":"OK"}' \
  --approve
```

Docker:

```bash
docker compose up --build urikvm
./scripts/call-http.sh
```

Real local control is possible with a platform-specific driver such as `pyautogui`, but it is intentionally disabled unless you pass `--allow-real` and use a trusted local profile. See `docs/SAFETY.md`.

Real mode:

```bash
pip install -e ".[real]"
./scripts/test-real.sh
# or:
URISYS_ALLOW_REAL=1 urisys-kvm --config config/kvm-profile.real.json \
  call kvm://local/monitor/primary/query/screenshot --approve --allow-real
```

Note: `ocr://` uses **Tesseract** and `llm://` uses **OpenAI vision** (or heuristic fallback) in the real profile. See `docs/OCR_LLM.md`.

```bash
pip install -e ".[real]"
# optional LiteLLM provider routing:
pip install -e ".[real,vision]"
export OPENAI_API_KEY=sk-...
./scripts/test-real.sh
```
