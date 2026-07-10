from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool


class ToolRegistry:
    _tools: dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> BaseTool | None:
        return cls._tools.get(name)

    @classmethod
    def get_all(cls) -> list[BaseTool]:
        return list(cls._tools.values())

    @classmethod
    def get_all_as_dict(cls) -> dict[str, Any]:
        return {
            name: {
                "name": tool.name,
                "description": tool.description,
                "args": tool.args if hasattr(tool, "args") else {},
            }
            for name, tool in cls._tools.items()
        }

    @classmethod
    def clear(cls) -> None:
        cls._tools.clear()


def tool_registry() -> ToolRegistry:
    return ToolRegistry
