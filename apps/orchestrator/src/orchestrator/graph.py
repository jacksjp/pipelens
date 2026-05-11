"""Orchestrator execution flow for lint analysis."""

import httpx
from common import AgentInput, AgentOutput, FindingsReport

from orchestrator.settings import settings


def run_lint(input_text: str) -> FindingsReport:
    """Call the lint-auditor agent and map its output into FindingsReport."""
    url = f"{settings.agent_lint_auditor_url.rstrip('/')}/execute"
    payload = AgentInput(text=input_text, metadata={}).model_dump()

    try:
        response = httpx.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        agent_output = AgentOutput.model_validate(response.json())
    except httpx.HTTPError as exc:
        return FindingsReport(
            agent="orchestrator",
            status="error",
            findings=[],
            improved_code=f"lint-auditor request failed: {exc}",
        )

    return FindingsReport(
        agent=agent_output.agent,
        status=agent_output.status,
        findings=agent_output.findings,
        improved_code=agent_output.output_text,
    )
