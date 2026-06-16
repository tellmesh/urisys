# uribrowser-docker

Portable `browser://` example for `urisys`.

```bash
python -m pip install -e .
urisys-browser call browser://default/page/command/open \
  --payload '{"url":"https://example.com"}' \
  --approve
```

Docker:

```bash
docker compose up --build uribrowser
curl -X POST http://127.0.0.1:8792/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"browser://default/page/command/open","payload":{"url":"https://example.com"},"context":{"approved":true}}'
```

The same `browser://` URI can be handled by mock, OS browser, Playwright, or a remote CDP bridge. See `docs/PORTABILITY.md`.

Real mode (Playwright):

```bash
pip install -e ".[real]"
python -m playwright install chromium
./scripts/test-real.sh
# or:
urisys-browser --config config/browser-profile.real.json call browser://default/page/command/open \
  --payload '{"url":"https://example.com"}' --approve --allow-real
```
