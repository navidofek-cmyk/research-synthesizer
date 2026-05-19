"""Tests for supervisor agent logic (mocking claude CLI calls)."""

import json
import pytest
from unittest.mock import patch


def mock_call(prompt, agent="supervisor", timeout=120):
    """Return predictable JSON or text depending on prompt content."""
    if "sub-topics" in prompt or "Break" in prompt:
        return '["topic A", "topic B", "topic C", "topic D"]'
    if "gaps" in prompt or "knowledge gaps" in prompt:
        return '[]'
    if "senior editor" in prompt or "Evaluate" in prompt:
        return '{"approved": true, "score": 8, "feedback": "OK"}'
    return "Synthesized research report content."


@patch("supervisor.claude_cli.call", side_effect=mock_call)
@patch("supervisor.research", return_value="Research summary for sub-topic.")
def test_run_returns_expected_keys(mock_research, mock_claude):
    from supervisor import run

    result = run("test topic")

    assert "topic" in result
    assert "sub_topics" in result
    assert "depth_gaps" in result
    assert "research" in result
    assert "report" in result


@patch("supervisor.claude_cli.call", side_effect=mock_call)
@patch("supervisor.research", return_value="Research summary.")
def test_run_calls_four_researchers(mock_research, mock_claude):
    from supervisor import run

    run("test topic")

    assert mock_research.call_count == 4


@patch("supervisor.claude_cli.call", side_effect=mock_call)
@patch("supervisor.research", return_value="Summary.")
def test_no_gaps_skips_followup(mock_research, mock_claude):
    from supervisor import run

    result = run("test topic")

    assert result["depth_gaps"] == []
    assert mock_research.call_count == 4  # no extra follow-up agents


def mock_call_with_gaps(prompt, agent="supervisor", timeout=120):
    if "Break" in prompt or "sub-topics" in prompt:
        return '["A", "B", "C", "D"]'
    if "gaps" in prompt or "knowledge gaps" in prompt:
        return '["follow-up question 1", "follow-up question 2"]'
    if "senior editor" in prompt or "Evaluate" in prompt:
        return '{"approved": true, "score": 8, "feedback": "OK"}'
    return "Final report."


@patch("supervisor.claude_cli.call", side_effect=mock_call_with_gaps)
@patch("supervisor.research", return_value="Summary.")
def test_gaps_trigger_followup_agents(mock_research, mock_claude):
    from supervisor import run

    result = run("test topic")

    assert len(result["depth_gaps"]) == 2
    assert mock_research.call_count == 6  # 4 initial + 2 follow-up


def mock_call_low_quality(prompt, agent="supervisor", timeout=120):
    if "Break" in prompt or "sub-topics" in prompt:
        return '["A", "B", "C", "D"]'
    if "gaps" in prompt or "knowledge gaps" in prompt:
        return '[]'
    if "senior editor" in prompt or "Evaluate" in prompt:
        return '{"approved": false, "score": 5, "feedback": "Too superficial, needs more depth."}'
    return "Draft report content."


@patch("supervisor.claude_cli.call", side_effect=mock_call_low_quality)
@patch("supervisor.research", return_value="Summary.")
def test_low_quality_triggers_revision(mock_research, mock_claude):
    from supervisor import run

    result = run("test topic")

    assert result["review"]["approved"] is False
    assert result["review"]["score"] == 5


@patch("supervisor.claude_cli.call", side_effect=mock_call)
@patch("supervisor.research", return_value="Summary.")
def test_review_included_in_result(mock_research, mock_claude):
    from supervisor import run

    result = run("test topic")

    assert "review" in result
    assert "score" in result["review"]
    assert "approved" in result["review"]
