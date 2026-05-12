"""Tests for lint-auditor executor with LLM integration."""

from unittest.mock import MagicMock, patch

import pytest
from agent_lint_auditor.card import CARD
from agent_lint_auditor.executor import execute
from common import AgentInput
from common.agent_runner import create_agent_app
from fastapi.testclient import TestClient


@pytest.fixture
def mock_agents_config():
    """Mock agents.yaml configuration."""
    return {
        "models": {
            "gpt-4": {
                "provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.2,
                "api_key_env": "OPENAI_API_KEY",
            },
            "claude-sonnet": {
                "provider": "anthropic",
                "model_name": "claude-3-5-sonnet-20241022",
                "temperature": 0.2,
                "api_key_env": "ANTHROPIC_API_KEY",
            },
        },
        "agents": {
            "lint-auditor": {
                "default_model": "claude-sonnet",
                "max_retries": 2,
                "description": "SQL and Python linting",
            }
        },
    }


def test_execute_with_config_error():
    """Test handling of missing config file."""
    payload = AgentInput(text="SELECT * FROM table")

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.side_effect = FileNotFoundError("agents.yaml not found")
        result = execute(payload)

    assert result.status == "error"
    assert any("Configuration error" in f.description for f in result.findings)


def test_execute_with_invalid_model(mock_agents_config):
    """Test handling of invalid model selection."""
    payload = AgentInput(text="SELECT * FROM table", metadata={"model": "non-existent-model"})

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.return_value = mock_agents_config
        with patch("agent_lint_auditor.executor.get_llm_for_agent") as mock_llm:
            mock_llm.side_effect = ValueError("Model 'non-existent-model' not found")
            result = execute(payload)

    assert result.status == "error"
    assert any("LLM initialization error" in f.description for f in result.findings)


def test_execute_uses_default_model(mock_agents_config):
    """Test that default model is used when not specified in metadata."""
    payload = AgentInput(text="def hello(): pass")

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.return_value = mock_agents_config
        with patch("agent_lint_auditor.executor.get_default_model_for_agent") as mock_default:
            mock_default.return_value = "claude-sonnet"
            with patch("agent_lint_auditor.executor.get_llm_for_agent") as mock_llm:
                mock_llm_instance = MagicMock()
                mock_llm.return_value = mock_llm_instance
                with patch("agent_lint_auditor.executor.run_lint_fix_graph") as mock_graph:
                    mock_graph.return_value = {
                        "initial_errors": [],
                        "fixed_errors": [],
                        "remaining_errors": [],
                        "final_code": "def hello(): pass",
                    }
                    result = execute(payload)

    mock_default.assert_called_once()
    assert result.status == "ok"


def test_execute_respects_model_from_metadata(mock_agents_config):
    """Test that model specified in metadata is used."""
    payload = AgentInput(text="def hello(): pass", metadata={"model": "gpt-4"})

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.return_value = mock_agents_config
        with patch("agent_lint_auditor.executor.get_llm_for_agent") as mock_llm:
            mock_llm_instance = MagicMock()
            mock_llm.return_value = mock_llm_instance
            with patch("agent_lint_auditor.executor.run_lint_fix_graph") as mock_graph:
                mock_graph.return_value = {
                    "initial_errors": [],
                    "fixed_errors": [],
                    "remaining_errors": [],
                    "final_code": "def hello(): pass",
                }
                result = execute(payload)

    # Verify gpt-4 was used
    mock_llm.assert_called_once_with("gpt-4", mock_agents_config)
    assert result.status == "ok"


def test_workflow_respects_max_retries(mock_agents_config):
    """Test that max_retries from config is passed to workflow."""
    payload = AgentInput(text="def hello(): pass")

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.return_value = mock_agents_config
        with patch("agent_lint_auditor.executor.get_default_model_for_agent") as mock_default:
            mock_default.return_value = "claude-sonnet"
            with patch("agent_lint_auditor.executor.get_llm_for_agent") as mock_llm:
                mock_llm_instance = MagicMock()
                mock_llm.return_value = mock_llm_instance
                with patch("agent_lint_auditor.executor.run_lint_fix_graph") as mock_graph:
                    mock_graph.return_value = {
                        "initial_errors": [],
                        "fixed_errors": [],
                        "remaining_errors": [],
                        "final_code": "def hello(): pass",
                    }
                    result = execute(payload)

    # Verify max_retries=2 was passed
    assert result.status == "ok"
    mock_graph.assert_called_once()
    call_kwargs = mock_graph.call_args[1]
    assert call_kwargs["max_retries"] == 2


def test_execute_converts_errors_to_findings(mock_agents_config):
    """Test that workflow errors are properly converted to findings."""
    payload = AgentInput(text="def hello(): pass")

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.return_value = mock_agents_config
        with patch("agent_lint_auditor.executor.get_default_model_for_agent") as mock_default:
            mock_default.return_value = "claude-sonnet"
            with patch("agent_lint_auditor.executor.get_llm_for_agent") as mock_llm:
                mock_llm_instance = MagicMock()
                mock_llm.return_value = mock_llm_instance
                with patch("agent_lint_auditor.executor.run_lint_fix_graph") as mock_graph:
                    mock_graph.return_value = {
                        "initial_errors": [
                            {
                                "line_no": 1,
                                "line_pos": 1,
                                "code": "E001",
                                "description": "Test error",
                            }
                        ],
                        "fixed_errors": [],
                        "remaining_errors": [],
                        "final_code": "def hello(): pass",
                    }
                    result = execute(payload)

    assert result.status == "ok"
    assert len(result.findings) >= 1
    assert any("linting" in f.description for f in result.findings)


def test_execute_returns_final_code(mock_agents_config):
    """Test that final code from workflow is returned as output_text."""
    payload = AgentInput(text="def hello(): pass")
    expected_code = "def hello():\n    pass"

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.return_value = mock_agents_config
        with patch("agent_lint_auditor.executor.get_default_model_for_agent") as mock_default:
            mock_default.return_value = "claude-sonnet"
            with patch("agent_lint_auditor.executor.get_llm_for_agent") as mock_llm:
                mock_llm_instance = MagicMock()
                mock_llm.return_value = mock_llm_instance
                with patch("agent_lint_auditor.executor.run_lint_fix_graph") as mock_graph:
                    mock_graph.return_value = {
                        "initial_errors": [],
                        "fixed_errors": [],
                        "remaining_errors": [],
                        "final_code": expected_code,
                    }
                    result = execute(payload)

    assert result.output_text == expected_code


def test_execute_endpoint_returns_lint_auditor_output(mock_agents_config) -> None:
    """The HTTP /execute endpoint should return lint-auditor AgentOutput payloads."""
    client = TestClient(create_agent_app(CARD, execute))

    with patch("agent_lint_auditor.executor.load_agents_config") as mock_load:
        mock_load.return_value = mock_agents_config
        with patch("agent_lint_auditor.executor.get_default_model_for_agent") as mock_default:
            mock_default.return_value = "claude-sonnet"
            with patch("agent_lint_auditor.executor.get_llm_for_agent") as mock_llm:
                mock_llm.return_value = MagicMock()
                with patch("agent_lint_auditor.executor.run_lint_fix_graph") as mock_graph:
                    mock_graph.return_value = {
                        "initial_errors": [],
                        "fixed_errors": [],
                        "remaining_errors": [],
                        "final_code": "SELECT 1;",
                        "fix_report": [],
                    }
                    res = client.post("/execute", json={"text": "select 1", "metadata": {}})

    assert res.status_code == 200
    assert res.json()["agent"] == "lint-auditor"
