"""Executor for the lint-auditor agent."""

from __future__ import annotations

import json
from typing import Any

from common import AgentInput, AgentOutput, Finding, Severity

from agent_lint_auditor.graph import run_lint_fix_graph
from agent_lint_auditor.llm_loader import (
    get_agent_config,
    get_default_model_for_agent,
    get_llm_for_agent,
    load_agents_config,
)
from agent_lint_auditor.settings import settings

# ===== Finding helpers =====


def _error_to_finding(
    error: dict[str, Any],
    severity: Severity,
    fix_entry: dict[str, Any] | None = None,
) -> Finding:
    """Convert a single lint error dict to a Finding.

    Args:
        error: Lint error with keys: code, description, line_no, line_pos.
        severity: Severity to assign.
        fix_entry: Optional fix_report entry with fix_applied + explanation fields.
    """
    code = str(error.get("code", "unknown"))
    description = str(error.get("description", "Lint issue"))
    line_no = error.get("line_no")
    line_pos = error.get("line_pos")

    snippet: str | None = f"line {line_no}:{line_pos or 1}" if line_no is not None else None

    suggested_fix: str | None = None
    if fix_entry:
        fix_applied = fix_entry.get("fix_applied", "")
        explanation = fix_entry.get("explanation", "")
        parts = [p for p in [fix_applied, explanation] if p]
        suggested_fix = " — ".join(parts) if parts else None
    elif severity == Severity.INFO:
        suggested_fix = f"Auto-fixed by linting tool. Rule {code}: {description}"

    prefix = "Auto-fixed" if severity == Severity.INFO else "Issue"
    return Finding(
        severity=severity,
        description=f"{prefix} [{code}]: {description}",
        original_snippet=snippet,
        suggested_fix=suggested_fix,
    )


def _build_fix_lookup(fix_report: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Build a dict keyed by rule_code for fast lookup during finding construction."""
    lookup: dict[str, dict[str, Any]] = {}
    for entry in fix_report:
        key = entry.get("rule_code", "")
        if key:
            lookup[key] = entry
    return lookup


# ===== Main executor =====


def execute(payload: AgentInput) -> AgentOutput:
    """Run the MCP-backed lint-fix workflow and return structured findings."""
    text = payload.text
    metadata = payload.metadata or {}

    # Load agents config
    try:
        agents_config = load_agents_config(settings.agents_config_path)
    except FileNotFoundError as e:
        return AgentOutput(
            agent="lint-auditor",
            status="error",
            findings=[
                Finding(
                    severity=Severity.CRITICAL,
                    description=f"Configuration error: {e}",
                    original_snippet=None,
                    suggested_fix=None,
                )
            ],
            output_text=None,
        )

    # Determine model
    model_name = metadata.get("model")
    if not model_name:
        try:
            model_name = get_default_model_for_agent(settings.agent_name, agents_config)
        except ValueError as e:
            return AgentOutput(
                agent="lint-auditor",
                status="error",
                findings=[
                    Finding(
                        severity=Severity.CRITICAL,
                        description=f"Model configuration error: {e}",
                        original_snippet=None,
                        suggested_fix=None,
                    )
                ],
                output_text=None,
            )

    # Get LLM instance
    try:
        llm = get_llm_for_agent(model_name, agents_config)
    except (ValueError, ImportError) as e:
        return AgentOutput(
            agent="lint-auditor",
            status="error",
            findings=[
                Finding(
                    severity=Severity.CRITICAL,
                    description=f"LLM initialization error: {e}",
                    original_snippet=None,
                    suggested_fix=None,
                )
            ],
            output_text=None,
        )

    agent_config = get_agent_config(settings.agent_name, agents_config)
    max_retries = agent_config.get("max_retries", 3)

    # Run the LangGraph workflow (MCP tool-calling + LLM explanation)
    try:
        result = run_lint_fix_graph(
            code=text,
            llm=llm,
            mcp_url=settings.mcp_server_url,
            max_retries=max_retries,
        )
    except Exception as e:
        return AgentOutput(
            agent="lint-auditor",
            status="error",
            findings=[
                Finding(
                    severity=Severity.CRITICAL,
                    description=f"Workflow execution error: {e}",
                    original_snippet=None,
                    suggested_fix=None,
                )
            ],
            output_text=None,
        )

    # Build findings from workflow result
    findings: list[Finding] = []
    fix_report: list[dict[str, Any]] = result.get("fix_report", [])
    fix_lookup = _build_fix_lookup(fix_report)

    # 1. Auto-fixed errors (resolved by MCP tools)
    for error in result.get("fixed_errors", []):
        code = str(error.get("code", "unknown"))
        fix_entry = fix_lookup.get(code)
        findings.append(_error_to_finding(error, Severity.INFO, fix_entry))

    # 2. LLM-fixed errors (resolved by LLM after tools couldn't)
    for entry in fix_report:
        if entry.get("category") == "llm-fixed":
            findings.append(
                Finding(
                    severity=Severity.INFO,
                    description=f"LLM-fixed [{entry.get('rule_code', '?')}]: {entry.get('original_error', '')}",
                    original_snippet=None,
                    suggested_fix=(
                        f"{entry.get('fix_applied', '')} — {entry.get('explanation', '')}"
                    ).strip(" —"),
                )
            )

    # 3. Unfixable issues (require schema/context not in the code)
    for entry in fix_report:
        if entry.get("category") == "unfixable":
            cannot_fix_reason = entry.get("cannot_fix_reason") or entry.get("explanation", "")
            findings.append(
                Finding(
                    severity=Severity.MEDIUM,
                    description=f"Cannot auto-fix [{entry.get('rule_code', '?')}]: {entry.get('original_error', '')}",
                    original_snippet=None,
                    suggested_fix=cannot_fix_reason,
                )
            )

    # Build output_text: final corrected code + structured fix report as JSON
    final_code = result.get("final_code", text)
    output_text = json.dumps(
        {
            "final_code": final_code,
            "fix_report": fix_report,
            "initial_error_count": len(result.get("initial_errors", [])),
            "auto_fixed_count": len(result.get("fixed_errors", [])),
            "remaining_count": len(result.get("remaining_errors", [])),
        },
        indent=2,
    )

    return AgentOutput(
        agent="lint-auditor",
        status="ok",
        findings=findings,
        output_text=output_text,
    )
