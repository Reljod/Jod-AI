from __future__ import annotations

from typing import Any

from langchain_core.tools import tool


@tool
async def execute_skill(
    skill_name: str,
    parameters: dict[str, Any],
) -> str:
    """Execute a named skill with the given parameters.

    Skills are specialized capabilities like code analysis, data processing,
    research, or custom workflows defined in the skills directory.

    Args:
        skill_name: The name of the skill to execute
        parameters: A dictionary of parameters to pass to the skill

    Returns:
        The result of the skill execution as a string
    """
    from app.skills.manager import get_skill_manager

    manager = get_skill_manager()
    return await manager.execute(skill_name, parameters)


@tool
async def list_skills() -> str:
    """List all available skills with their names and descriptions."""
    from app.skills.manager import get_skill_manager

    manager = get_skill_manager()
    skills = manager.list_skills()
    if not skills:
        return "No skills are currently loaded."

    lines = ["**Available Skills:**"]
    for s in skills:
        lines.append(f"- **{s['name']}**: {s['description']}")
    return "\n".join(lines)
