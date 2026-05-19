"""Tests for MCP server tools (web search, cache)."""

import pytest
from pathlib import Path
from mcp_server import web_search, save_report, get_cached


def test_web_search_returns_results():
    result = web_search("Python programming language", max_results=2)
    assert len(result) > 50
    assert "Python" in result


def test_web_search_no_results_returns_message():
    result = web_search("xyzzy123nonexistent987qwerty", max_results=1)
    assert isinstance(result, str)
    assert len(result) > 0


def test_save_and_get_cached(tmp_path, monkeypatch):
    import mcp_server
    monkeypatch.setattr(mcp_server, "CACHE_DIR", tmp_path)

    save_report("Test Topic", "This is test content.")
    result = get_cached("Test Topic")
    assert "test content" in result


def test_get_cached_missing_returns_message(tmp_path, monkeypatch):
    import mcp_server
    monkeypatch.setattr(mcp_server, "CACHE_DIR", tmp_path)

    result = get_cached("nonexistent topic xyz")
    assert "No cached" in result
