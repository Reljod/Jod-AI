from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.core.llm import list_available_models

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
async def get_models() -> dict[str, list[dict[str, Any]]]:
    models = await list_available_models()
    return {"models": models}


@router.get("/default")
async def get_default_model() -> dict[str, str]:
    from app.config.settings import get_settings

    settings = get_settings()
    return {"model": settings.openrouter_default_model}
