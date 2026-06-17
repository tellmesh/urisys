# uriocr

`ocr://` URI capability pack (text + word boxes) for
[`urisys-node`](https://github.com/tellmesh/urisys).

Provides `ocr://{host}/.../query/text` and image-to-text queries backed by
`tesseract` (via `pytesseract` + `Pillow`), with a mock driver when no real
backend is available.

```bash
pip install "uriocr[real]"
```

Loaded into a node either at boot (`URISYS_NODE_PACKS=...,ocr`) or hot-loaded over
the wire (`POST /uri/pack {"pack":"ocr"}`). See the urisys docs for the full
capability model.

Licensed under Apache-2.0.
