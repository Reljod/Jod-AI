from __future__ import annotations

from fastapi import APIRouter

from app.tools.registry import ToolRegistry

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("")
async def list_tools():
    if not ToolRegistry.get_all():
        from app.core.agent import _register_default_tools
        _register_default_tools()

    return {
        "tools": ToolRegistry.get_all_as_dict()
    }
