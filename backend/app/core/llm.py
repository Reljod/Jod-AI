from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage

from app.config.settings import get_settings

settings = get_settings()


@lru_cache(maxsize=32)
def get_chat_model(
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> BaseChatModel:
    model_name = model or settings.openrouter_default_model
    temp = temperature if temperature is not None else settings.openrouter_temperature
    mt = max_tokens or settings.openrouter_max_tokens

    return init_chat_model(
        model=model_name,
        model_provider="openai",
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        temperature=temp,
        max_tokens=mt,
        model_kwargs={
            "extra_headers": {
                "HTTP-Referer": settings.openrouter_site_url or "https://jod-ai.local",
                "X-Title": settings.openrouter_site_name or "Jod-AI",
            }
        },
    )


async def list_available_models() -> list[dict[str, Any]]:
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.openrouter_base_url}/models",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "id": m["id"],
                "name": m.get("name", m["id"]),
                "provider": m.get("provider", {}).get("providerName", "unknown"),
                "description": m.get("description", ""),
                "pricing": {
                    "prompt": m.get("pricing", {}).get("prompt", 0),
                    "completion": m.get("pricing", {}).get("completion", 0),
                },
                "context_length": m.get("context_length", 0),
            }
            for m in data.get("data", [])
        ]


async def count_tokens(messages: list[BaseMessage]) -> int:
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        text = " ".join(m.content if isinstance(m.content, str) else str(m.content) for m in messages)
        return len(encoding.encode(text))
    except Exception:
        return sum(len(m.content) if isinstance(m.content, str) else 0 for m in messages) // 2
