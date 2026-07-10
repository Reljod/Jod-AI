from __future__ import annotations

from langchain_core.tools import tool


@tool
async def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d %H:%M:%S UTC")


@tool
async def think(reasoning: str) -> str:
    """Use this tool to engage in chain-of-thought reasoning.

    Before using any other tool, take a moment to reason about the task.
    Break down complex problems step by step.

    Args:
        reasoning: Your step-by-step reasoning about the current task

    Returns:
        Confirmation that reasoning was noted
    """
    return f"Reasoning noted. Continue with the plan based on this analysis."
