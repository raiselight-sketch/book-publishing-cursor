from __future__ import annotations

import os
from typing import Any

from litellm import completion


def _ollama_base() -> str | None:
    return os.environ.get("OLLAMA_API_BASE", "http://127.0.0.1:11434")


def complete_chat(
    model: str,
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.35,
    max_tokens: int = 8192,
) -> str:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if model.startswith("ollama/"):
        kwargs["api_base"] = _ollama_base()
    resp = completion(**kwargs)
    choice = resp.choices[0]
    msg = choice.message
    content = getattr(msg, "content", None) or ""
    return content if isinstance(content, str) else str(content)
