"""
Claude Code CLI wrapper for non-interactive agent calls.

Each agent type has:
  - system_prompt : defines its role and skills
  - allowed_tools : explicit permission list (principle of least privilege)
  - model         : sonnet for supervisor reasoning, haiku for parallel workers
"""

import subprocess
import time

# ── Agent definitions ──────────────────────────────────────────────────────────

AGENTS = {
    "supervisor": {
        "model": "sonnet",
        "allowed_tools": [],           # text-only: no file/bash access needed
        "system_prompt": (
            "You are a Research Supervisor agent. "
            "Your skills: strategic planning, research decomposition, "
            "quality evaluation, and synthesis of complex information. "
            "You coordinate specialist research agents and produce "
            "structured, accurate, and well-reasoned analytical reports. "
            "Always return valid JSON when asked for structured output."
        ),
    },
    "researcher": {
        "model": "haiku",
        "allowed_tools": [],           # text-only: web search handled externally
        "system_prompt": (
            "You are a specialist Research Agent. "
            "Your skills: analysing web search results, extracting key facts, "
            "identifying statistics and recent developments, and producing "
            "concise, factual summaries. "
            "Focus strictly on your assigned sub-topic. Be thorough and precise."
        ),
    },
}

# ── CLI call ───────────────────────────────────────────────────────────────────

def call(
    prompt: str,
    agent: str = "supervisor",
    timeout: int = 120,
) -> str:
    """
    Run a claude CLI agent in non-interactive mode.

    Builds: claude -p --model <m> --allowedTools <t> --append-system-prompt <s> <prompt>
    Retries up to 3 times on transient failures.
    """
    cfg = AGENTS[agent]
    model = cfg["model"]
    system_prompt = cfg["system_prompt"]
    allowed_tools = cfg["allowed_tools"]

    cmd = ["claude", "-p", "--model", model]

    if allowed_tools:
        cmd += ["--allowedTools", *allowed_tools]
    else:
        # No tools — block everything for least-privilege execution
        cmd += ["--allowedTools", ""]

    cmd += ["--append-system-prompt", system_prompt]
    cmd += [prompt]

    for attempt in range(3):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0:
                return result.stdout.strip()

            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(
                f"claude CLI exited {result.returncode}: {result.stderr.strip()}"
            )

        except subprocess.TimeoutExpired:
            if attempt < 2:
                time.sleep(5)
                continue
            raise RuntimeError(f"claude CLI timed out after {timeout}s")

    raise RuntimeError("claude CLI failed after 3 attempts")
