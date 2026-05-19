"""Tests for claude_cli wrapper — agent config and command building."""

import pytest
from claude_cli import AGENTS, call
from unittest.mock import patch, MagicMock


def test_agents_have_required_keys():
    for name, cfg in AGENTS.items():
        assert "model" in cfg, f"{name} missing model"
        assert "system_prompt" in cfg, f"{name} missing system_prompt"
        assert "allowed_tools" in cfg, f"{name} missing allowed_tools"
        assert "mcp_config" in cfg, f"{name} missing mcp_config"


def test_supervisor_uses_sonnet():
    assert AGENTS["supervisor"]["model"] == "sonnet"


def test_researcher_uses_haiku():
    assert AGENTS["researcher"]["model"] == "haiku"


def test_researcher_has_mcp_config():
    assert AGENTS["researcher"]["mcp_config"] is not None


def test_supervisor_has_no_mcp():
    assert AGENTS["supervisor"]["mcp_config"] is None


@patch("subprocess.run")
def test_call_builds_correct_command(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")

    call("test prompt", agent="supervisor")

    cmd = mock_run.call_args[0][0]
    assert "claude" in cmd
    assert "-p" in cmd
    assert "--model" in cmd
    assert "sonnet" in cmd
    assert "--append-system-prompt" in cmd


@patch("subprocess.run")
def test_researcher_call_includes_mcp(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")

    call("test prompt", agent="researcher")

    cmd = mock_run.call_args[0][0]
    assert "--mcp-config" in cmd


@patch("subprocess.run")
def test_supervisor_call_excludes_mcp(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")

    call("test prompt", agent="supervisor")

    cmd = mock_run.call_args[0][0]
    assert "--mcp-config" not in cmd
