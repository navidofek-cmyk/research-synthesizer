#!/usr/bin/env python3
"""
Research Synthesizer — Multi-Agent Supervisor System
Demonstrates: Supervisor pattern + Parallel workflow + Conditional branching
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

import supervisor as sup

console = Console()


def print_header(topic: str) -> None:
    console.print()
    console.print(Panel(
        Text.assemble(
            ("Research Synthesizer\n", "bold blue"),
            ("Multi-Agent Supervisor System\n\n", "dim"),
            ("Supervisor:   ", "dim"), ("Claude Sonnet 4.6\n", "bold"),
            ("Researchers:  ", "dim"), ("Claude Haiku 4.5 (parallel)\n", "bold"),
            ("Patterns:     ", "dim"), ("Supervisor · Parallel · Conditional\n\n", "bold"),
            ("Topic: ", "dim"), (topic, "bold yellow"),
        ),
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Research Synthesizer — Multi-Agent Supervisor System"
    )
    parser.add_argument("topic", help="Research topic to investigate")
    parser.add_argument(
        "-o", "--output",
        help="Save Markdown report to file",
        default=None
    )
    args = parser.parse_args()

    print_header(args.topic)

    phases_done = []
    agents_done = []

    def on_phase(msg: str) -> None:
        phases_done.append(msg)
        console.print(f"[bold cyan]→[/bold cyan] {msg}")

    def on_agent_done(sub_topic: str) -> None:
        agents_done.append(sub_topic)
        short = sub_topic[:72] + ("…" if len(sub_topic) > 72 else "")
        console.print(f"  [green]✓[/green] {short}")

    try:
        result = sup.run(
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

    summary_lines = [
        f"Sub-topics researched: {len(result['sub_topics'])}",
        f"Total agents used:     {len(result['research'])}",
        f"Follow-up gaps found:  {len(result['depth_gaps'])}",
    ]
    console.print(Panel(
        "\n".join(summary_lines),
        title="[dim]Run summary[/dim]",
        border_style="dim",
        padding=(0, 2)
    ))

    if args.output:
        output_path = Path(args.output)
        header = (
            f"# Research Report: {result['topic']}\n"
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
            f"---\n\n"
        )
        output_path.write_text(header + result["report"])
        console.print(f"\n[green]Report saved →[/green] {output_path}")


if __name__ == "__main__":
    main()
