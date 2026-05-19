"""Thin wrapper around the claude CLI for non-interactive use."""

import subprocess
import time

SUPERVISOR_MODEL = "sonnet"
RESEARCHER_MODEL = "haiku"


def call(prompt: str, model: str = SUPERVISOR_MODEL, timeout: int = 120) -> str:
    """
    Run `claude -p --model <model> <prompt>` and return stdout.
    Retries up to 3 times on transient failures.
    """
    for attempt in range(3):
        try:
            result = subprocess.run(
                ["claude", "-p", "--model", model, prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()

            stderr = result.stderr.strip()
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"claude CLI exited {result.returncode}: {stderr}")

        except subprocess.TimeoutExpired:
            if attempt < 2:
                time.sleep(5)
                continue
            raise RuntimeError(f"claude CLI timed out after {timeout}s")

    raise RuntimeError("claude CLI failed after 3 attempts")
