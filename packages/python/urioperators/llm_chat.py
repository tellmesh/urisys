from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from urioperators.llm_json import parse_json_response


def openai_compatible_chat(
    messages: list[dict[str, Any]],
    model: str,
    api_key: str,
    base_url: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 1024,
    timeout: float = 90.0,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return parse_json_response(data["choices"][0]["message"]["content"])


def litellm_chat(
    messages: list[dict[str, Any]],
    model: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    try:
        import litellm  # type: ignore
    except Exception as exc:
        raise RuntimeError("litellm driver requires: pip install litellm") from exc
    response = litellm.completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return parse_json_response(response.choices[0].message.content)
