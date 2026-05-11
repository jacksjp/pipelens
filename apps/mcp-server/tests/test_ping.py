"""Smoke test for the MCP server ping tool."""

from mcp_server.server import ping


def test_ping_returns_pong() -> None:
    """The ping tool returns the literal string 'pong'."""
    assert ping() == "pong"
