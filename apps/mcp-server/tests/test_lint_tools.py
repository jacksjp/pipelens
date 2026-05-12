"""Contract tests for MCP lint-fix tools."""

from mcp_server.server import lint_fix_python, lint_fix_sql

EXPECTED_KEYS = {"initial_errors", "fixed_errors", "final_chunk", "final_errors"}


def test_lint_fix_sql_contract() -> None:
    sql_text = "\nselect 1"

    result = lint_fix_sql(sql_text, user_dialect="snowflake")

    assert set(result.keys()) == EXPECTED_KEYS
    assert isinstance(result["initial_errors"], list)
    assert isinstance(result["fixed_errors"], list)
    assert isinstance(result["final_errors"], list)
    assert isinstance(result["final_chunk"], str)
    assert len(result["final_errors"]) <= len(result["initial_errors"])


def test_lint_fix_python_contract() -> None:
    python_text = "import os\n"

    result = lint_fix_python(python_text)

    assert set(result.keys()) == EXPECTED_KEYS
    assert isinstance(result["initial_errors"], list)
    assert isinstance(result["fixed_errors"], list)
    assert isinstance(result["final_errors"], list)
    assert isinstance(result["final_chunk"], str)
    assert len(result["final_errors"]) <= len(result["initial_errors"])
