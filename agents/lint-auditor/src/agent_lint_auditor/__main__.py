"""Entry point for the lint-auditor agent."""

import uvicorn
from common.agent_runner import create_agent_app

from agent_lint_auditor.card import CARD
from agent_lint_auditor.executor import execute
from agent_lint_auditor.settings import settings

app = create_agent_app(CARD, execute)


def main() -> None:
    """Start the lint-auditor agent HTTP server."""
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
