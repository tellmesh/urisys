# urioperators

Shared pure helpers extracted from `urillm` and `urirdp_llm` handlers (JSON parsing,
OpenAI-compatible chat, LiteLLM chat, plan/decide normalizers).

Used by capability packs via `PYTHONPATH` (`packages/python`) or editable install.
No runtime dependency on `urisysedge` — packs keep their own env/display adapters.
