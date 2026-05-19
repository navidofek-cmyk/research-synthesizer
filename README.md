# Research Synthesizer

Multi-agent research system using the **Claude Code CLI** as the AI backend.  
**No API key needed** — uses your existing Claude Code authentication.

---

## Zadání (Robot Dreams — Vibe Coding HW01)

> Vytvořte projekt s praktickým použitím SDK pro kódovacích agentů. Cílem je, aby projekt demonstroval libovolnou orchestraci (workflow nebo multi-agent) a zároveň měl praktické použití.
>
> **Kódovací agent:** Claude Code CLI  
> **Maximální počet bodů:** 100

### Splněné požadavky

| Požadavek | Řešení |
|-----------|--------|
| SDK kódovacího agenta | `claude -p` CLI (Claude Code) — bez API klíče |
| Praktické použití | Výzkumný asistent: zadáš téma, dostaneš strukturovaný report |
| Multi-agent: **Supervisor** | Claude Sonnet koordinuje celý pipeline |
| Workflow: **Paralelní** | Research agenti (Claude Haiku) běží současně |
| Workflow: **Conditional** | Supervisor vyhodnotí mezery → spustí follow-up agenty jen pokud jsou potřeba |
| Workflow: **Sekvenční** | Plánování → výzkum → evaluace → syntéza |

---

## Architecture

```
User Input (topic)
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  SUPERVISOR  (claude --model sonnet)                │
│                                                     │
│  1. Generate 4 sub-topics        [Sequential]       │
│  2. Dispatch to researchers      [Parallel]         │
│  3. Check for depth gaps         [Conditional]      │
│  4. Follow-up research if needed [Cond. Parallel]   │
│  5. Synthesize final report      [Sequential]       │
└─────────────────────────────────────────────────────┘
         │         │         │         │
         ▼         ▼         ▼         ▼
    ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
    │ R1  │   │ R2  │   │ R3  │   │ R4  │   Research Agents
    └─────┘   └─────┘   └─────┘   └─────┘   (claude --model haiku)
    each agent: DuckDuckGo search → claude synthesis
```

### Orchestration Patterns

| Pattern | Where |
|---------|-------|
| **Supervisor** | Sonnet agent plans, evaluates, synthesizes |
| **Parallel** | Haiku agents run simultaneously via `ThreadPoolExecutor` |
| **Conditional** | Supervisor checks coverage → spawns follow-up only if gaps found |
| **Sequential** | Planning → Research → Evaluation → Synthesis pipeline |

### How it works (no API key)

Each "agent" is a `claude -p --model <model> "<prompt>"` subprocess call.  
Web search uses DuckDuckGo (free, no API key).  
LLM calls use the claude CLI which authenticates via your existing Claude Code session.

## Setup

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (no API key config needed)
uv sync

# Make sure claude CLI is authenticated
claude  # login if needed
```

## Usage

```bash
# Basic research
uv run python main.py "climate change impact on agriculture"

# Save report to file
uv run python main.py "quantum computing" -o report.md

# More examples
uv run python main.py "history of artificial intelligence"
uv run python main.py "renewable energy technologies 2025"
```

## Example Output

```
→ Supervisor: analyzing topic and creating research plan
→ Launching 4 parallel research agents
  ✓ Current state of quantum computing hardware
  ✓ Quantum algorithms and their applications
  ✓ Quantum computing companies and investment landscape
  ✓ Challenges and timeline to quantum advantage
→ Supervisor: checking for knowledge gaps [conditional]
→ Coverage complete — no follow-up needed
→ Supervisor: synthesizing final report

────────── Final Report ──────────

# Quantum Computing: A Comprehensive Research Report
...
```

## Files

| File | Description |
|------|-------------|
| `main.py` | CLI entry point with rich terminal output |
| `supervisor.py` | Supervisor agent — orchestrates the pipeline |
| `researcher.py` | Research agent — DuckDuckGo + claude synthesis |
| `claude_cli.py` | Wrapper for `claude -p` subprocess calls |
| `tools.py` | DuckDuckGo web search (no API key) |
