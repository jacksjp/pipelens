"""FastMCP server skeleton for the Code Critic system.

Exposes lightweight lint/fix tools for SQL and Python snippets.
"""

from typing import Any

from fastmcp import FastMCP

from mcp_server.lint_validators.python_lint_checker import lint_fix_python as run_python_lint_fix
from mcp_server.settings import settings
from mcp_server.lint_validators.sql_lint_checker import lint_fix_sql as run_sql_lint_fix

mcp = FastMCP("code-critic")


@mcp.tool()
def ping() -> str:
    """Trivial liveness tool used by tests and smoke checks."""
    return "pong"


@mcp.tool()
def lint_fix_sql(sql_text: str, user_dialect: str | None = None) -> dict[str, Any]:
    """Run SQLFluff lint/fix/lint and return a normalized state payload."""
    return run_sql_lint_fix(sql_text=sql_text, user_dialect=user_dialect)


@mcp.tool()
def lint_fix_python(python_text: str) -> dict[str, Any]:
    """Run Ruff lint/fix/lint and return a normalized state payload."""
    return run_python_lint_fix(python_text=python_text)


def main() -> None:
    """Run the MCP server over streamable-http transport."""
    mcp.run(
        transport="streamable-http",
        host=settings.host,
        port=settings.port,
        path=settings.path,
    )


if __name__ == "__main__":
    main()
