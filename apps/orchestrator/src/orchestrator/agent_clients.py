"""HTTP client helpers for orchestrator downstream services."""

from orchestrator.settings import settings


def agent_urls() -> dict[str, str]:
    """Return the configured base URL for each downstream agent."""
    return {
        "lint-auditor": settings.agent_lint_auditor_url,
    }
