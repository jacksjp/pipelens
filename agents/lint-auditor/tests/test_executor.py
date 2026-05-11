"""Smoke tests for the lint-auditor executor and HTTP surface."""

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from agent_lint_auditor.card import CARD
from agent_lint_auditor.executor import detect_input_kind, execute
from common import AgentInput
from common.agent_runner import create_agent_app
from fastapi.testclient import TestClient


def test_detect_input_kind_variants() -> None:
    """Input classification should detect sql, python, and mixed snippets."""
    assert detect_input_kind("select * from users") == "sql"
    assert detect_input_kind("def hello():\n    print('ok')") == "python"
    assert detect_input_kind("def run():\n    cursor.execute('select 1')") == "mixed"


def test_executor_mixed_input_calls_both_linters(monkeypatch: Any) -> None:
    """Mixed payloads should produce findings from both SQL and Python tool calls."""

    def fake_call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "lint_fix_sql":
            return {
                "initial_errors": [{"code": "LT01", "description": "spacing"}],
                "fixed_errors": [{"code": "LT01", "description": "spacing"}],
                "final_errors": [],
                "final_chunk": "SELECT 1;",
            }
        assert tool_name == "lint_fix_python"
        assert "python_text" in arguments
        return {
            "initial_errors": [{"code": "F401", "description": "unused import"}],
            "fixed_errors": [],
            "final_errors": [],
            "final_chunk": "print('ok')\n",
        }

    monkeypatch.setattr("agent_lint_auditor.executor._call_tool", fake_call_tool)

    out = execute(AgentInput(text="def run():\n    cursor.execute('select 1')", metadata={}))
    assert out.agent == "lint-auditor"
    assert out.status == "ok"
    assert len(out.findings) >= 2
    assert any("[sql]" in finding.description for finding in out.findings)
    assert any("[python]" in finding.description for finding in out.findings)


def test_execute_endpoint_returns_lint_auditor_output(monkeypatch: Any) -> None:
    """The HTTP /execute endpoint should return lint-auditor AgentOutput payloads."""

    def fake_call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "lint_fix_sql":
            return {
                "initial_errors": [],
                "fixed_errors": [],
                "final_errors": [],
                "final_chunk": "SELECT 1;",
            }
        return {
            "initial_errors": [],
            "fixed_errors": [],
            "final_errors": [],
            "final_chunk": arguments.get("python_text", ""),
        }

    monkeypatch.setattr("agent_lint_auditor.executor._call_tool", fake_call_tool)

    client = TestClient(create_agent_app(CARD, execute))
    res = client.post("/execute", json={"text": "select 1", "metadata": {}})
    assert res.status_code == 200
    assert res.json()["agent"] == "lint-auditor"
