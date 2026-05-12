"""Orchestrator execution flow for lint analysis."""

import httpx
import yaml
from common import AgentInput, AgentOutput, FindingsReport

from orchestrator.settings import settings

_DEFAULT_CLIENT_TIMEOUT = 600.0  # 10 minutes


def _agent_timeout(agent_name: str) -> float:
    """Read client_timeout_seconds for the given agent from agents.yaml."""
    try:
        with open(settings.agents_config_path, encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
        return float(
            config.get("agents", {})
            .get(agent_name, {})
            .get("client_timeout_seconds", _DEFAULT_CLIENT_TIMEOUT)
        )
    except Exception:
        return _DEFAULT_CLIENT_TIMEOUT


def run_lint(input_text: str) -> FindingsReport:
    """Call the lint-auditor agent and map its output into FindingsReport."""
    url = f"{settings.agent_lint_auditor_url.rstrip('/')}/execute"
    payload = AgentInput(text=input_text, metadata={}).model_dump()
    timeout = _agent_timeout("lint-auditor")

    try:
        response = httpx.post(url, json=payload, timeout=timeout)
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
