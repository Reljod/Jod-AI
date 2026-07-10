from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool

from app.config.settings import get_settings

settings = get_settings()


def _get_workspace() -> Path:
    path = Path(settings.file_storage_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _resolve_path(path: str) -> Path:
    workspace = _get_workspace().resolve()
    full_path = (workspace / path).resolve()
    try:
        full_path.relative_to(workspace)
    except ValueError:
        raise PermissionError(f"Access denied: {path} is outside the workspace") from None
    return full_path


@tool
async def read_file(path: str) -> str:
    """Read the contents of a file.

    Args:
        path: Relative path to the file within the workspace

    Returns:
        The contents of the file as a string
    """
    full_path = _resolve_path(path)
    if not full_path.exists():
        return f"Error: File not found: {path}"
    if not full_path.is_file():
        return f"Error: Not a file: {path}"

    try:
        content = full_path.read_text(encoding="utf-8")
        return content
    except UnicodeDecodeError:
        return f"Error: Cannot read binary file: {path}"


@tool
async def write_file(path: str, content: str) -> str:
    """Write content to a file (creates parent directories if needed).

    Args:
        path: Relative path to the file within the workspace
        content: The text content to write

    Returns:
        Confirmation message with file path
    """
    full_path = _resolve_path(path)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} bytes to {path}"


@tool
async def list_files(path: str = "") -> str:
    """List files and directories at the given path.

    Args:
        path: Relative path to list (empty for workspace root)

    Returns:
        Directory listing as formatted text
    """
    full_path = _resolve_path(path) if path else _get_workspace()
    if not full_path.exists():
        return f"Error: Path not found: {path}"
    if not full_path.is_dir():
        return f"Not a directory: {path}"

    entries = sorted(full_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    lines = [f"Contents of /{path or ''}:"]
    for entry in entries:
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"  {entry.name}{suffix}")

    return "\n".join(lines) if len(lines) > 1 else "Directory is empty."


@tool
async def delete_file(path: str) -> str:
    """Delete a file or empty directory.

    Args:
        path: Relative path to the file or directory to delete

    Returns:
        Confirmation message
    """
    full_path = _resolve_path(path)
    if not full_path.exists():
        return f"Error: Not found: {path}"

    if full_path.is_file():
        size = full_path.stat().st_size
        full_path.unlink()
        return f"Deleted file {path} ({size} bytes)"
    elif full_path.is_dir():
        full_path.rmdir()
        return f"Deleted empty directory {path}"
    else:
        return f"Error: Cannot delete {path}"


@tool
async def search_files(pattern: str, path: str = "") -> str:
    """Search for files matching a glob pattern.

    Args:
        pattern: Glob pattern to search for (e.g., '**/*.py', '*.json')
        path: Relative path to search in (empty for workspace root)

    Returns:
        Matching file paths
    """
    search_path = _resolve_path(path) if path else _get_workspace()
    matches = list(search_path.glob(pattern))
    if not matches:
        return f"No files matching '{pattern}' found in /{path}"

    lines = [f"Files matching '{pattern}' in /{path} ({len(matches)}):"]
    for m in matches:
        try:
            rel = m.relative_to(_get_workspace())
            lines.append(f"  {rel}")
        except ValueError:
            lines.append(f"  {m.name}")

    return "\n".join(lines)
