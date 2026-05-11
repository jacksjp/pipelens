"""Entry point for the lint-auditor agent."""

from common.agent_runner import run_agent

from agent_lint_auditor.card import CARD
from agent_lint_auditor.executor import execute
from agent_lint_auditor.settings import settings


def main() -> None:
    """Start the lint-auditor agent HTTP server."""
    run_agent(CARD, execute, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
