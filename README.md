# Research Synthesizer

Multi-agent research system built with the **Anthropic Claude SDK**.  
Demonstrates **Supervisor + Parallel + Conditional** orchestration patterns.

## Architecture

```
User Input (topic)
      │
      ▼
┌─────────────────────────────────────────────┐
│  SUPERVISOR  (Claude Sonnet 4.6)            │
│                                             │
│  1. Generate 4 sub-topics  [Sequential]     │
│  2. Dispatch to researchers [Parallel]      │
│  3. Check depth gaps        [Conditional]   │
│  4. Follow-up research      [Conditional    │
│                              Parallel]      │
│  5. Synthesize report       [Sequential]    │
└─────────────────────────────────────────────┘
         │    │    │    │
         ▼    ▼    ▼    ▼
    ┌────┐ ┌────┐ ┌────┐ ┌────┐
    │ R1 │ │ R2 │ │ R3 │ │ R4 │   Research Agents
    └────┘ └────┘ └────┘ └────┘   (Claude Haiku 4.5)
    each uses web_search tool
```

### Orchestration Patterns Used

| Pattern | Where |
|---------|-------|
| **Supervisor** | Central Claude Sonnet agent coordinates all sub-agents |
| **Parallel** | 4 researcher agents run simultaneously via `ThreadPoolExecutor` |
| **Conditional** | Supervisor evaluates coverage → spawns follow-up agents only if gaps found |
| **Sequential** | Planning → Research → Evaluation → Synthesis pipeline |

## Setup

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install deps
uv sync

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
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
  ✓ Quantum computing companies and investment
  ✓ Challenges and timeline to quantum advantage
→ Supervisor: checking for knowledge gaps (conditional step)
→ Coverage complete — no follow-up needed
→ Supervisor: synthesizing final report

────────── Final Report ──────────

# Quantum Computing: Comprehensive Research Report
...
```

## Files

| File | Description |
|------|-------------|
| `main.py` | CLI entry point with rich terminal output |
| `supervisor.py` | Supervisor agent — orchestrates the pipeline |
| `researcher.py` | Research agent — web search + summarization |
| `tools.py` | Web search tool (DuckDuckGo, no API key needed) |

## Key Design Decisions

- **Supervisor uses Sonnet** for complex reasoning (planning, evaluation, synthesis)
- **Researchers use Haiku** for cost-efficient parallel execution
- **No API key for search** — uses DuckDuckGo via `duckduckgo-search`
- **Conditional depth check** — avoids unnecessary agent calls when coverage is good
