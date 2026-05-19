# Research Synthesizer — Claude Code Project

## What this project does

Multi-agent research pipeline using **Claude Code CLI** as the AI backend.
User provides a topic → system produces a structured Markdown research report.
No API key needed — authentication via existing Claude Code session.

## Project structure

```
research-synthesizer/
├── main.py          # CLI entry point (rich terminal output)
├── supervisor.py    # Supervisor agent — planning, evaluation, synthesis
├── researcher.py    # Research agent — web search + summarization
├── claude_cli.py    # Wrapper: claude -p --model --allowedTools --append-system-prompt
├── tools.py         # DuckDuckGo search (ddgs, no API key)
├── pyproject.toml   # uv project config
├── CLAUDE.md        # This file
└── .claude/
    ├── settings.json       # Project permissions, hooks, env
    └── settings.local.json # Local session permissions (not committed)
```

## How to run

```bash
uv sync                                          # install deps
uv run python main.py "quantum computing"        # research a topic
uv run python main.py "topic" -o report.md       # save to file
```

## Agent profiles

Defined in `claude_cli.py` — each agent has a model, system prompt (skills), and allowed tools.

| Agent | Model | Skills | Permissions |
|-------|-------|--------|-------------|
| `supervisor` | sonnet | Planning, decomposition, quality evaluation, synthesis | text-only (`--allowedTools ""`) |
| `researcher` | haiku | Web result analysis, fact extraction, summarization | text-only (`--allowedTools ""`) |

## Orchestration patterns

| Pattern | Where in code |
|---------|--------------|
| **Supervisor** | `supervisor.py` — Sonnet coordinates all sub-agents |
| **Parallel** | `run_parallel_research()` — `ThreadPoolExecutor` |
| **Conditional** | `check_depth_gaps()` — follow-up agents only if gaps found |
| **Sequential** | `run()` — plan → research → evaluate → synthesize |

## Dependencies

| Package | Purpose |
|---------|---------|
| `ddgs` | DuckDuckGo web search (free, no API key) |
| `rich` | Terminal output formatting |
| `claude` CLI | LLM calls — must be authenticated |

## Key design decisions

- **Sonnet for supervisor** — complex reasoning, JSON planning, synthesis
- **Haiku for researchers** — fast parallel execution, cost-efficient
- **Least-privilege permissions** — agents blocked from file/bash tools
- **Python handles web search** — results passed to agents via prompt
- **uv for packaging** — fast dependency resolution

## Settings (.claude/settings.json)

- Default model: `claude-sonnet-4-6`
- Allowed bash commands: `uv`, `git`, `python`, `claude -p`
- Denied: `rm -rf`, `curl`, `wget`, `sudo`
- Env: `PYTHONPATH=.`, `PYTHONDONTWRITEBYTECODE=1`
- Hook: logs every Bash tool call before execution
