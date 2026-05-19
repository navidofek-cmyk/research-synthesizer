"""
Research Agent — uses MCP web_search tool directly during reasoning.

Architecture with MCP:
  claude haiku → calls mcp__research-tools__web_search() autonomously
               → decides when/what to search based on findings
               → produces final summary

No pre-fetching in Python — the agent drives its own research process.
"""

import claude_cli


def research(sub_topic: str, main_topic: str) -> str:
    """
    Research agent: autonomously searches and summarizes via MCP tool.
    Claude decides search queries and iterations based on what it finds.
    """
    prompt = (
        f"Research this sub-topic for a report on '{main_topic}':\n\n"
        f"**Sub-topic:** {sub_topic}\n\n"
        f"Instructions:\n"
        f"1. Use web_search at least 2-3 times with different, specific queries\n"
        f"2. Read the results carefully and follow up on interesting findings\n"
        f"3. Synthesize everything into a comprehensive summary covering:\n"
        f"   - Key facts and statistics\n"
        f"   - Recent developments (2024-2025)\n"
        f"   - Important context and implications\n"
        f"   - Notable controversies or open questions\n\n"
        f"Be thorough and factual. Cite sources where relevant."
    )

    return claude_cli.call(prompt, agent="researcher", timeout=120)
