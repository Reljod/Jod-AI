from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from typing import Any


class SkillDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        handler: Any,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.handler = handler
        self.parameters = parameters or {}


class SkillManager:
    _skills: dict[str, SkillDefinition] = {}

    def register(self, skill: SkillDefinition) -> None:
        self._skills[skill.name] = skill

    def register_from_module(self, module_path: str) -> None:
        path = Path(module_path)
        if not path.exists():
            raise FileNotFoundError(f"Skill module not found: {module_path}")

        spec = importlib.util.spec_from_file_location(path.stem, path)
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load skill module: {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module):
            if hasattr(obj, "_is_skill"):
                self.register(SkillDefinition(
                    name=getattr(obj, "_skill_name", name),
                    description=getattr(obj, "_skill_description", ""),
                    handler=obj,
                    parameters=getattr(obj, "_skill_parameters", {}),
                ))

    def get(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def list_skills(self) -> list[dict[str, Any]]:
        return [
            {
                "name": s.name,
                "description": s.description,
                "parameters": s.parameters,
            }
            for s in self._skills.values()
        ]

    async def execute(self, name: str, parameters: dict[str, Any]) -> str:
        skill = self.get(name)
        if not skill:
            return f"Error: Skill '{name}' not found. Available: {', '.join(self._skills)}"

        try:
            if inspect.iscoroutinefunction(skill.handler):
                result = await skill.handler(**parameters)
            else:
                result = skill.handler(**parameters)
            return str(result)
        except Exception as e:
            return f"Error executing skill '{name}': {e!s}"

    def load_skills_directory(self, directory: str) -> int:
        path = Path(directory)
        if not path.exists():
            return 0

        count = 0
        for file in path.glob("*.py"):
            if file.name.startswith("_"):
                continue
            try:
                self.register_from_module(str(file))
                count += 1
            except Exception:
                pass
        return count


_manager: SkillManager | None = None


def get_skill_manager() -> SkillManager:
    global _manager
    if _manager is None:
        _manager = SkillManager()
    return _manager


def skill(
    name: str | None = None,
    description: str = "",
    parameters: dict[str, Any] | None = None,
):
    """Decorator to mark a function as a skill."""
    def decorator(func):
        func._is_skill = True
        func._skill_name = name or func.__name__
        func._skill_description = description or func.__doc__ or ""
        func._skill_parameters = parameters or {}
        return func
    return decorator
