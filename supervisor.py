"""
Supervisor Agent — orchestrates parallel research agents via claude CLI.

Patterns demonstrated:
  Sequential  — planning → research → evaluation → synthesis pipeline
  Parallel    — researcher agents run concurrently (ThreadPoolExecutor)
  Conditional — depth-gap check decides whether follow-up agents are spawned
  Supervisor  — this module coordinates all sub-agents
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import claude_cli
from researcher import research


def generate_sub_topics(topic: str) -> list[str]:
    """Supervisor breaks research topic into focused sub-topics."""
    prompt = (
        f"Break the research topic '{topic}' into exactly 4 focused sub-topics "
        f"that together provide comprehensive coverage.\n\n"
        f"Return ONLY a valid JSON array of 4 strings. No explanation, no markdown."
    )
    text = claude_cli.call(prompt)
    start, end = text.find("["), text.rfind("]") + 1
    return json.loads(text[start:end])


def run_parallel_research(
    topic: str,
    sub_topics: list[str],
    on_done: Callable[[str], None] | None = None,
) -> dict[str, str]:
    """Dispatch sub-topics to researcher agents running in parallel."""
    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=len(sub_topics)) as executor:
        future_to_topic = {
            executor.submit(research, st, topic): st
            for st in sub_topics
        }
        for future in as_completed(future_to_topic):
            st = future_to_topic[future]
            results[st] = future.result()
            if on_done:
                on_done(st)

    return results


def check_depth_gaps(topic: str, results: dict[str, str]) -> list[str]:
    """
    Conditional check: identify knowledge gaps requiring follow-up research.
    Returns up to 2 follow-up questions, or empty list if coverage is sufficient.
    """
    summaries = "\n".join(f"- {k}: {v[:300]}..." for k, v in results.items())
    prompt = (
        f"Topic: '{topic}'\n\nResearch summaries so far:\n{summaries}\n\n"
        f"Identify up to 2 specific knowledge gaps that need deeper research "
        f"to complete the picture. If coverage is sufficient, return [].\n\n"
        f"Return ONLY a valid JSON array of strings (specific questions to research). "
        f"Maximum 2 items. No explanation."
    )
    text = claude_cli.call(prompt)
    start, end = text.find("["), text.rfind("]") + 1
    gaps = json.loads(text[start:end])
    return gaps[:2]


def synthesize(topic: str, all_research: dict[str, str]) -> str:
    """Supervisor synthesizes all research into a structured Markdown report."""
    sections = "\n\n".join(
        f"### Research: {k}\n{v}" for k, v in all_research.items()
    )
    prompt = (
        f"You are a senior research analyst. Specialist research agents have gathered "
        f"the following information about: **{topic}**\n\n"
        f"---\n{sections}\n---\n\n"
        f"Synthesize all findings into a comprehensive Markdown report with:\n"
        f"1. **Executive Summary** (2-3 paragraphs)\n"
        f"2. **Key Findings** (bullet points organized by theme)\n"
        f"3. **Detailed Analysis** (in-depth coverage, cross-reference sub-topics)\n"
        f"4. **Conclusions & Implications**\n\n"
        f"Do not just list each section separately — synthesize across all research."
    )
    return claude_cli.call(prompt, timeout=180)


def run(
    topic: str,
    on_phase: Callable[[str], None] | None = None,
    on_research_done: Callable[[str], None] | None = None,
) -> dict:
    """Full supervisor pipeline. Returns results dict with report."""

    if on_phase:
        on_phase("Supervisor: analyzing topic and creating research plan")
    sub_topics = generate_sub_topics(topic)

    if on_phase:
        on_phase(f"Launching {len(sub_topics)} parallel research agents")
    results = run_parallel_research(topic, sub_topics, on_done=on_research_done)

    if on_phase:
        on_phase("Supervisor: checking for knowledge gaps [conditional]")
    gaps = check_depth_gaps(topic, results)

    if gaps:
        if on_phase:
            on_phase(f"Gaps found — launching {len(gaps)} targeted follow-up agents")
        extra = run_parallel_research(topic, gaps, on_done=on_research_done)
        results.update({f"[follow-up] {k}": v for k, v in extra.items()})
    else:
        if on_phase:
            on_phase("Coverage complete — no follow-up needed")

    if on_phase:
        on_phase("Supervisor: synthesizing final report")
    report = synthesize(topic, results)

    return {
        "topic": topic,
        "sub_topics": sub_topics,
        "depth_gaps": gaps,
        "research": results,
        "report": report,
    }
