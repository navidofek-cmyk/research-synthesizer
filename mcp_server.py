"""
MCP Server — Research Tools

Exposes tools that researcher agents call directly during their reasoning:
  - web_search(query, max_results)  — DuckDuckGo search
  - save_report(topic, content)     — persist report to disk
  - get_cached(topic)               — retrieve previously saved research

Agents connect via: claude -p --mcp-config .claude/mcp_config.json
"""

import json
import re
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from ddgs import DDGS

mcp = FastMCP("research-tools")

CACHE_DIR = Path(".cache/research")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _topic_key(topic: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", topic.lower().strip())[:80]


@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo. No API key required.
    Returns formatted results with title, snippet, and source URL.
    Use specific queries for best results. Call multiple times with different queries.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"No results found for: {query}"

        formatted = []
        for r in results:
            formatted.append(
                f"**{r.get('title', 'No title')}**\n"
                f"{r.get('body', '')}\n"
                f"Source: {r.get('href', '')}"
            )
        return "\n\n---\n\n".join(formatted)

    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def save_report(topic: str, content: str) -> str:
    """
    Save a research report to disk for later retrieval.
    Returns the file path where the report was saved.
    """
    key = _topic_key(topic)
    path = CACHE_DIR / f"{key}.md"
    path.write_text(f"# {topic}\n\n{content}")
    return f"Report saved to {path}"


@mcp.tool()
def get_cached(topic: str) -> str:
    """
    Retrieve previously saved research for a topic.
    Returns the cached content or a message if nothing is cached.
    """
    key = _topic_key(topic)
    path = CACHE_DIR / f"{key}.md"
    if path.exists():
        return path.read_text()
    return f"No cached research found for: {topic}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
