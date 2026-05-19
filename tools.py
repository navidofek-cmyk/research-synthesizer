"""Web search tool implementation using DuckDuckGo (no API key required)."""

import time
from ddgs import DDGS

TOOL_DEFINITION = {
    "name": "web_search",
    "description": (
        "Search the web for current information about a topic. "
        "Use specific, focused queries for best results."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }
}


def web_search(query: str, max_results: int = 5) -> str:
    """Execute web search and return formatted results."""
    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return f"No results found for: {query}"

            formatted = []
            for r in results:
                title = r.get("title", "No title")
                body = r.get("body", "No content")
                href = r.get("href", "")
                formatted.append(f"**{title}**\n{body}\nSource: {href}")

            return "\n\n---\n\n".join(formatted)

        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return f"Search failed after retries: {str(e)}"
