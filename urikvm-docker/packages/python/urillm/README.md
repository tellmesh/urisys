# urillm

`llm://` URI capability pack (vision analysis + heuristic planning) for
[`urisys-node`](https://github.com/tellmesh/urisys).

Provides `llm://{host}/.../query/...` for vision-grounded UI analysis and step
planning. Works heuristically out of the box; with the `vision` extra it can use
an OpenAI-compatible or LiteLLM backend.

```bash
pip install "urillm[vision]"
```

Loaded into a node either at boot (`URISYS_NODE_PACKS=...,llm`) or hot-loaded over
the wire (`POST /uri/pack {"pack":"llm"}`). See the urisys docs for the full
capability model.

Licensed under Apache-2.0.
