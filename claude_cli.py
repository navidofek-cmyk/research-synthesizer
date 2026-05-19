"""
Claude Code CLI wrapper for non-interactive agent calls.

Each agent type has:
  - system_prompt  : defines its role and skills
  - allowed_tools  : explicit permission list (principle of least privilege)
  - mcp_config     : optional MCP server config for tool access
  - model          : sonnet for supervisor reasoning, haiku for parallel workers
"""

import subprocess
import time
from pathlib import Path

MCP_CONFIG = str(Path(__file__).parent / ".claude" / "mcp_config.json")

# ── Agent definitions ──────────────────────────────────────────────────────────

AGENTS = {
    "supervisor": {
        "model": "sonnet",
        "allowed_tools": [],
        "mcp_config": None,            # supervisor only needs text generation
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
        "allowed_tools": ["mcp__research-tools__web_search"],
        "mcp_config": MCP_CONFIG,      # researcher actively calls web_search via MCP
        "system_prompt": (
            "You are a specialist Research Agent with access to a web_search tool. "
            "Your skills: web research, fact extraction, source evaluation, summarization. "
            "Always use web_search 2-3 times with different queries before summarizing. "
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

    Supervisor: claude -p --model sonnet --allowedTools "" --append-system-prompt ...
    Researcher: claude -p --model haiku  --allowedTools mcp__web_search
                        --mcp-config .claude/mcp_config.json --append-system-prompt ...
    """
    cfg = AGENTS[agent]
    model = cfg["model"]
    system_prompt = cfg["system_prompt"]
    allowed_tools = cfg["allowed_tools"]
    mcp_config = cfg["mcp_config"]

    cmd = ["claude", "-p", "--model", model]

    if allowed_tools:
        cmd += ["--allowedTools"] + allowed_tools
    else:
        cmd += ["--allowedTools", ""]

    if mcp_config:
        cmd += ["--mcp-config", mcp_config]

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
