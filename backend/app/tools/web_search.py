from __future__ import annotations

from langchain_core.tools import tool


@tool
async def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for current information.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default 5)

    Returns:
        Search results with titles, snippets, and URLs
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://lite.duckduckgo.com/lite/",
                params={"q": query},
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; Jod-AI/1.0)",
                },
            )
            resp.raise_for_status()

            import re

            html = resp.text
            results = re.findall(
                r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                html,
                re.DOTALL,
            )
            snippets = re.findall(
                r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
                html,
                re.DOTALL,
            )

            lines = [f"Search results for: {query}"]
            for i, (url, title) in enumerate(results[:max_results]):
                clean_title = re.sub(r"<[^>]+>", "", title).strip()
                snippet = ""
                if i < len(snippets):
                    snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip()
                lines.append(f"\n{i + 1}. {clean_title}")
                lines.append(f"   URL: {url}")
                if snippet:
                    lines.append(f"   {snippet}")

            if not results:
                return f"No search results found for: {query}"

            return "\n".join(lines)

    except Exception as e:
        return f"Web search failed: {e!s}"
