# Research Synthesizer

> Multi-agent research system powered by **Claude Code CLI**.  
> Give it a topic → get a structured research report. No API key needed.

---

## How it works

```
╔══════════════════════════════════════════════════════════════════╗
║                        YOUR TOPIC                               ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │
                           ▼
          ┌────────────────────────────────┐
          │   SUPERVISOR  (claude sonnet)  │  ← plans, evaluates, synthesizes
          └──────────────┬─────────────────┘
                         │
              [1] Generate sub-topics
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐   ...up to 4 agents
   │ AGENT 1  │    │ AGENT 2  │    │ AGENT 3  │   (claude haiku)
   │          │    │          │    │          │
   │ DDG ×3   │    │ DDG ×3   │    │ DDG ×3   │   ← parallel web search
   │ synthesize│   │ synthesize│   │ synthesize│
   └────┬─────┘    └────┬─────┘    └────┬─────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
              [2] Collect results
                        │
                        ▼
          ┌─────────────────────────────┐
          │  Supervisor: gaps check?    │  ← conditional step
          └──────────┬──────────────────┘
                     │
           ┌─────────┴──────────┐
     gaps? YES                  NO
           │                    │
           ▼                    │
   ┌────────────────┐           │
   │ follow-up      │           │
   │ agents (×1-2)  │           │
   └───────┬────────┘           │
           └──────────┬─────────┘
                      │
              [3] Synthesize
                      │
                      ▼
          ┌───────────────────────┐
          │   FINAL REPORT (.md)  │
          └───────────────────────┘
```

---

## Pipeline at a glance

| Step | Agent | Pattern | What happens |
|------|-------|---------|--------------|
| 1 | Supervisor (Sonnet) | Sequential | Breaks topic into 4 focused sub-topics |
| 2 | Researchers (Haiku ×4) | **Parallel** | Each searches DuckDuckGo 3× and summarizes |
| 3 | Supervisor (Sonnet) | Conditional | Checks if any knowledge gaps remain |
| 4 | Follow-up agents (Haiku ×0-2) | Cond. Parallel | Fills gaps — only runs if needed |
| 5 | Supervisor (Sonnet) | Sequential | Synthesizes all findings into a Markdown report |

---

## Example run

```
$ uv run python main.py "artificial intelligence in healthcare"

╭──────────────────────────────────────────────────────╮
│  Research Synthesizer                                │
│  Supervisor:   claude sonnet                         │
│  Researchers:  claude haiku  (parallel)              │
│  Web search:   DuckDuckGo    (no API key needed)     │
│  Topic: artificial intelligence in healthcare        │
╰──────────────────────────────────────────────────────╯

→ Supervisor: analyzing topic and creating research plan
→ Launching 4 parallel research agents
  ✓ AI-powered diagnostic imaging and disease detection
  ✓ Predictive analytics and patient outcome modeling
  ✓ Ethical, regulatory, and data privacy challenges
  ✓ Machine learning for drug discovery and clinical trials
→ Supervisor: checking for knowledge gaps [conditional]
→ Gaps found — launching 2 targeted follow-up agents
  ✓ FDA-approved AI diagnostic tools in clinical use
  ✓ Regulatory frameworks: EU AI Act, FDA SaMD, HIPAA
→ Supervisor: synthesizing final report

─────────────────────── Final Report ───────────────────────

# Artificial Intelligence in Healthcare
## Executive Summary
...

╭─────────────────────╮
│ Sub-topics:    4    │
│ Total agents:  6    │
│ Follow-ups:    2    │
╰─────────────────────╯
```

---

## Setup

```bash
# 1. Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and install dependencies
git clone https://github.com/your-username/research-synthesizer
cd research-synthesizer
uv sync

# 3. Make sure Claude Code CLI is authenticated
claude        # opens interactive session — log in if needed
```

## Usage

```bash
# Research any topic
uv run python main.py "quantum computing"

# Save report to Markdown file
uv run python main.py "climate change" -o report.md

# More examples
uv run python main.py "history of the internet"
uv run python main.py "renewable energy technologies 2025"
```

---

## Files

| File | Description |
|------|-------------|
| `main.py` | CLI entry point, rich terminal output |
| `supervisor.py` | Supervisor agent — planning, evaluation, synthesis |
| `researcher.py` | Research agent — web search + claude summarization |
| `claude_cli.py` | Thin wrapper around `claude -p --model` subprocess |
| `tools.py` | DuckDuckGo search (no API key required) |

---

## Agent profiles

Each agent runs with explicit skills and permissions (`claude_cli.py`):

| Agent | Model | Skills | Allowed tools |
|-------|-------|--------|---------------|
| **Supervisor** | Sonnet | Planning · decomposition · quality evaluation · synthesis | none (text-only) |
| **Researcher** | Haiku | Web result analysis · fact extraction · concise summarization | none (web search handled externally) |

Permissions follow the **principle of least privilege** — agents get only what they need.  
Web search is executed in Python (DuckDuckGo), results are passed to the agent via prompt.

---

## Tech stack

| Component | Tool |
|-----------|------|
| LLM (supervisor) | Claude Sonnet via `claude` CLI |
| LLM (researchers) | Claude Haiku via `claude` CLI |
| Web search | DuckDuckGo (`ddgs`) — free, no API key |
| Parallelism | Python `ThreadPoolExecutor` |
| CLI output | `rich` |
| Package manager | `uv` |

---

---

## CZ — Zadání (Robot Dreams · Vibe Coding HW01)

> Vytvořte projekt s praktickým použitím SDK pro kódovacích agentů. Cílem je demonstrovat orchestraci (workflow nebo multi-agent) a zároveň mít praktické použití.
>
> **Kódovací agent:** Claude Code CLI · **Max. bodů:** 100

### Splněné požadavky

| Požadavek | Řešení |
|-----------|--------|
| SDK kódovacího agenta | `claude -p` CLI (Claude Code) — bez API klíče |
| Praktické použití | Výzkumný asistent: téma → strukturovaný Markdown report |
| Multi-agent: **Supervisor** | Claude Sonnet koordinuje celý pipeline |
| Workflow: **Paralelní** | Research agenti (Haiku) běží současně |
| Workflow: **Conditional** | Supervisor spustí follow-up agenty jen pokud jsou mezery |
| Workflow: **Sekvenční** | Plánování → výzkum → evaluace → syntéza |
