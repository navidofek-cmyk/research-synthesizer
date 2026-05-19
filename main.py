#!/usr/bin/env python3
"""
Research Synthesizer — Multi-Agent Supervisor System
Uses claude CLI (no API key needed) + DuckDuckGo web search.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

import supervisor

console = Console()


def print_header(topic: str) -> None:
    console.print()
    console.print(Panel(
        Text.assemble(
            ("Research Synthesizer\n", "bold blue"),
            ("Multi-Agent Supervisor System\n\n", "dim"),
            ("Supervisor:   ", "dim"), ("claude sonnet  (orchestration + synthesis)\n", "bold"),
            ("Researchers:  ", "dim"), ("claude haiku   (parallel web research)\n", "bold"),
            ("Web search:   ", "dim"), ("DuckDuckGo     (no API key needed)\n", "bold"),
            ("Patterns:     ", "dim"), ("Supervisor · Parallel · Conditional · Sequential\n\n", "bold"),
            ("Topic: ", "dim"), (topic, "bold yellow"),
        ),
        border_style="blue",
        padding=(1, 2),
    ))
    console.print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Research Synthesizer — Multi-Agent Supervisor System"
    )
    parser.add_argument("topic", help="Research topic to investigate")
    parser.add_argument("-o", "--output", help="Save Markdown report to file", default=None)
    args = parser.parse_args()

    print_header(args.topic)

    def on_phase(msg: str) -> None:
        console.print(f"[bold cyan]→[/bold cyan] {msg}")

    def on_agent_done(sub_topic: str) -> None:
        short = sub_topic[:72] + ("…" if len(sub_topic) > 72 else "")
        console.print(f"  [green]✓[/green] {short}")

    try:
        result = supervisor.run(
            args.topic,
            on_phase=on_phase,
            on_research_done=on_agent_done,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)

    console.print()
    console.print(Rule("[bold]Final Report[/bold]", style="blue"))
    console.print()
    console.print(Markdown(result["report"]))
    console.print()

    console.print(Panel(
        "\n".join([
            f"Sub-topics researched: {len(result['sub_topics'])}",
            f"Total agents used:     {len(result['research'])}",
            f"Follow-up gaps found:  {len(result['depth_gaps'])}",
        ]),
        title="[dim]Run summary[/dim]",
        border_style="dim",
        padding=(0, 2),
    ))

    if args.output:
        path = Path(args.output)
        header = (
            f"# Research Report: {result['topic']}\n"
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
        )
        path.write_text(header + result["report"])
        console.print(f"\n[green]Report saved →[/green] {path}")


if __name__ == "__main__":
    main()
