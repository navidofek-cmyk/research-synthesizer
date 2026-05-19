"""Research Agent — specialist sub-agent that investigates a single sub-topic."""

import anthropic
from tools import TOOL_DEFINITION, web_search

MODEL = "claude-haiku-4-5-20251001"
MAX_TOOL_ROUNDS = 4


def research(client: anthropic.Anthropic, sub_topic: str, main_topic: str) -> str:
    """
    Research agent that uses web search to investigate a sub-topic.
    Returns a detailed summary string.
    """
    messages = [
        {
            "role": "user",
            "content": (
                f"You are a specialist research agent investigating: '{main_topic}'\n\n"
                f"Your assigned sub-topic: **{sub_topic}**\n\n"
                f"Instructions:\n"
                f"1. Use web_search 2-3 times with different queries to gather comprehensive info\n"
                f"2. Synthesize what you find into a clear, factual summary\n"
                f"3. Include key statistics, recent developments, and important context\n"
                f"4. Be thorough but focused on this specific sub-topic"
            )
        }
    ]

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            tools=[TOOL_DEFINITION],
            messages=messages
        )

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = web_search(
                    block.input["query"],
                    block.input.get("max_results", 5)
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    return "".join(
        block.text for block in response.content
        if hasattr(block, "text")
    )
