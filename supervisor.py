"""
Supervisor Agent — orchestrates parallel research agents and synthesizes results.

Pattern: Multi-Agent Supervisor
  1. Generate sub-topics (sequential)
  2. Dispatch researcher agents (parallel)
  3. Evaluate depth gaps (conditional)
  4. Additional targeted research if needed (conditional parallel)
  5. Synthesize final report (sequential)
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import anthropic
from researcher import research

MODEL = "claude-sonnet-4-6"


class ResearchSupervisor:
    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def generate_sub_topics(self, topic: str) -> list[str]:
        """Break research topic into focused sub-topics."""
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    f"Break the research topic '{topic}' into exactly 4 focused sub-topics "
                    f"that together provide comprehensive coverage.\n\n"
                    f"Return ONLY a valid JSON array of 4 strings. No explanation."
                )
            }]
        )
        text = response.content[0].text.strip()
        start, end = text.find("["), text.rfind("]") + 1
        return json.loads(text[start:end])

    def run_parallel_research(
        self,
        topic: str,
        sub_topics: list[str],
        on_done: Callable[[str], None] | None = None
    ) -> dict[str, str]:
        """Dispatch sub-topics to researcher agents running in parallel."""
        results: dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=len(sub_topics)) as executor:
            future_to_topic = {
                executor.submit(research, self.client, st, topic): st
                for st in sub_topics
            }
            for future in as_completed(future_to_topic):
                st = future_to_topic[future]
                results[st] = future.result()
                if on_done:
                    on_done(st)

        return results

    def check_depth_gaps(self, topic: str, results: dict[str, str]) -> list[str]:
        """
        Conditional check: identify knowledge gaps that need deeper research.
        Returns list of follow-up questions (empty if coverage is sufficient).
        """
        summaries = "\n".join(
            f"- {k}: {v[:300]}..." for k, v in results.items()
        )
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": (
                    f"Topic: '{topic}'\n\nResearch summaries:\n{summaries}\n\n"
                    f"Identify up to 2 specific knowledge gaps that need deeper research "
                    f"to complete the picture. If coverage is sufficient, return [].\n\n"
                    f"Return ONLY a JSON array of strings (specific research questions). "
                    f"Maximum 2 items."
                )
            }]
        )
        text = response.content[0].text.strip()
        start, end = text.find("["), text.rfind("]") + 1
        gaps = json.loads(text[start:end])
        return gaps[:2]

    def synthesize(self, topic: str, all_research: dict[str, str]) -> str:
        """Supervisor synthesizes all research into a structured report."""
        research_sections = "\n\n".join(
            f"### Research: {k}\n{v}" for k, v in all_research.items()
        )

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": (
                    f"You are a senior research analyst. Based on findings from multiple "
                    f"specialist research agents, create a comprehensive report on:\n\n"
                    f"**{topic}**\n\n"
                    f"---\n{research_sections}\n---\n\n"
                    f"Write a well-structured report in Markdown with:\n"
                    f"1. **Executive Summary** (2-3 paragraphs)\n"
                    f"2. **Key Findings** (bullet points organized by theme)\n"
                    f"3. **Detailed Analysis** (in-depth coverage)\n"
                    f"4. **Conclusions & Implications**\n\n"
                    f"Synthesize across all research — don't just list each section separately."
                )
            }]
        )
        return response.content[0].text


def run(
    topic: str,
    on_phase: Callable[[str], None] | None = None,
    on_research_done: Callable[[str], None] | None = None
) -> dict:
    """
    Main entry point. Runs the full supervisor pipeline and returns results dict.
    """
    client = anthropic.Anthropic()
    supervisor = ResearchSupervisor(client)

    if on_phase:
        on_phase("Supervisor: analyzing topic and creating research plan")
    sub_topics = supervisor.generate_sub_topics(topic)

    if on_phase:
        on_phase(f"Launching {len(sub_topics)} parallel research agents")
    results = supervisor.run_parallel_research(topic, sub_topics, on_done=on_research_done)

    if on_phase:
        on_phase("Supervisor: checking for knowledge gaps (conditional step)")
    gaps = supervisor.check_depth_gaps(topic, results)

    if gaps:
        if on_phase:
            on_phase(f"Gaps found — launching {len(gaps)} targeted follow-up agents")
        extra = supervisor.run_parallel_research(topic, gaps, on_done=on_research_done)
        results.update({f"[follow-up] {k}": v for k, v in extra.items()})
    else:
        if on_phase:
            on_phase("Coverage complete — no follow-up needed")

    if on_phase:
        on_phase("Supervisor: synthesizing final report")
    report = supervisor.synthesize(topic, results)

    return {
        "topic": topic,
        "sub_topics": sub_topics,
        "depth_gaps": gaps,
        "research": results,
        "report": report
    }
