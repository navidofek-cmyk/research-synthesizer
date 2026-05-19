"""
Research Agent — searches DuckDuckGo and uses claude CLI to synthesize findings.
No API key required: web search is free, LLM is via local claude CLI auth.
"""

from tools import web_search
import claude_cli

NUM_SEARCHES = 3


def _build_search_queries(sub_topic: str, main_topic: str) -> list[str]:
    """Generate diverse search queries for a sub-topic."""
    return [
        f"{sub_topic} {main_topic}",
        f"{sub_topic} latest developments 2025",
        f"{sub_topic} key facts statistics",
    ]


def research(sub_topic: str, main_topic: str) -> str:
    """
    Research agent: web search → claude synthesis.
    Returns a detailed summary string.
    """
    queries = _build_search_queries(sub_topic, main_topic)

    search_results = []
    for q in queries[:NUM_SEARCHES]:
        result = web_search(q, max_results=4)
        search_results.append(f"Search: '{q}'\n{result}")

    context = "\n\n===\n\n".join(search_results)

    prompt = (
        f"You are a specialist research agent. Your task is to analyze web search results "
        f"and produce a comprehensive research summary.\n\n"
        f"Main research topic: {main_topic}\n"
        f"Your assigned sub-topic: {sub_topic}\n\n"
        f"Web search results:\n{context}\n\n"
        f"Based on these results, provide:\n"
        f"1. Key facts and statistics\n"
        f"2. Recent developments (2024-2025)\n"
        f"3. Important context and implications\n"
        f"4. Any notable controversies or open questions\n\n"
        f"Be thorough, factual, and focused on this specific sub-topic."
    )

    return claude_cli.call(prompt, agent="researcher", timeout=90)
