"""Executor for the lint-auditor agent."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Literal

from common import AgentInput, AgentOutput, Finding, Severity
from fastmcp import Client

from agent_lint_auditor.settings import settings

InputKind = Literal["sql", "python", "mixed", "unknown"]

SQL_KEYWORD_RE = re.compile(
    r"\b(select|from|where|insert|update|delete|create|with|join|group\s+by|order\s+by)\b",
    flags=re.IGNORECASE,
)
PYTHON_MARKER_RE = re.compile(
    r"(^\s*(def|class|import|from)\s+)|\bprint\s*\(|__name__\s*==\s*['\"]__main__['\"]",
    flags=re.IGNORECASE | re.MULTILINE,
)
EXECUTE_SQL_RE = re.compile(
    r"\bexecute\(\s*(?P<quote>'''|\"\"\"|'|\")(?P<body>.*?)(?P=quote)\s*\)",
    flags=re.IGNORECASE | re.DOTALL,
)
TRIPLE_STRING_RE = re.compile(
    r"(?P<quote>'''|\"\"\")(?P<body>.*?)(?P=quote)",
    flags=re.DOTALL,
)


def detect_input_kind(text: str) -> InputKind:
    """Classify input text into SQL, Python, mixed, or unknown."""
    has_sql = bool(SQL_KEYWORD_RE.search(text))
    has_python = bool(PYTHON_MARKER_RE.search(text))

    if has_sql and has_python:
        return "mixed"
    if has_sql:
        return "sql"
    if has_python:
        return "python"
    return "unknown"


def extract_sql_snippets_from_python(text: str) -> list[str]:
    """Extract likely SQL snippets from Python code blocks and execute calls."""
    snippets: list[str] = []

    for match in EXECUTE_SQL_RE.finditer(text):
        candidate = match.group("body").strip()
        if candidate and SQL_KEYWORD_RE.search(candidate):
            snippets.append(candidate)

    for match in TRIPLE_STRING_RE.finditer(text):
        candidate = match.group("body").strip()
        if candidate and SQL_KEYWORD_RE.search(candidate):
            snippets.append(candidate)

    deduped: list[str] = []
    seen: set[str] = set()
    for snippet in snippets:
        if snippet not in seen:
            deduped.append(snippet)
            seen.add(snippet)
    return deduped


async def _invoke_tool_async(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call one MCP tool and return a normalized dictionary payload."""
    async with Client(settings.mcp_server_url) as client:
        result = await client.call_tool(tool_name, arguments)
    return _normalize_tool_payload(result)


def _normalize_tool_payload(result: object) -> dict[str, Any]:
    """Extract dict payload from FastMCP CallToolResult variants."""
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured

    structured_alt = getattr(result, "structured_content", None)
    if isinstance(structured_alt, dict):
        return structured_alt

    content = getattr(result, "content", None)
    if isinstance(content, list):
        for item in content:
            text = getattr(item, "text", None)
            if not isinstance(text, str):
                continue
            try:
                maybe_payload = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(maybe_payload, dict):
                return maybe_payload

    return {}


def _errors_to_findings(errors: list[dict[str, Any]], source: str, severity: Severity) -> list[Finding]:
    findings: list[Finding] = []
    for error in errors:
        code = str(error.get("code", "unknown"))
        description = str(error.get("description", "Lint issue"))
        line_no = error.get("line_no")
        line_pos = error.get("line_pos")
        snippet: str | None = None
        if line_no is not None:
            snippet = f"{source} line {line_no}:{line_pos or 1}"

        prefix = "Auto-fixed" if severity == Severity.INFO else "Issue"
        findings.append(
            Finding(
                severity=severity,
                description=f"{prefix} [{source}] {code}: {description}",
                original_snippet=snippet,
                suggested_fix=None,
            )
        )
    return findings


def _call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Synchronous wrapper around asynchronous FastMCP calls."""
    return asyncio.run(_invoke_tool_async(tool_name, arguments))


def execute(payload: AgentInput) -> AgentOutput:
    """Run linting for SQL, Python, or mixed input and return findings."""
    text = payload.text
    dialect = payload.metadata.get("dialect")
    kind = detect_input_kind(text)

    findings: list[Finding] = []
    fixed_chunks: list[str] = []

    if kind in {"sql", "mixed"}:
        sql_inputs = [text] if kind == "sql" else extract_sql_snippets_from_python(text)
        for sql_input in sql_inputs:
            if not sql_input.strip():
                continue
            sql_result = _call_tool(
                "lint_fix_sql",
                {"sql_text": sql_input, "user_dialect": dialect},
            )
            findings.extend(_errors_to_findings(sql_result.get("fixed_errors", []), "sql", Severity.INFO))
            findings.extend(
                _errors_to_findings(sql_result.get("initial_errors", []), "sql", Severity.LOW)
            )
            findings.extend(_errors_to_findings(sql_result.get("final_errors", []), "sql", Severity.LOW))
            final_chunk = sql_result.get("final_chunk")
            if isinstance(final_chunk, str) and final_chunk.strip():
                fixed_chunks.append(final_chunk)

    if kind in {"python", "mixed", "unknown"}:
        python_result = _call_tool("lint_fix_python", {"python_text": text})
        findings.extend(_errors_to_findings(python_result.get("fixed_errors", []), "python", Severity.INFO))
        findings.extend(_errors_to_findings(python_result.get("initial_errors", []), "python", Severity.LOW))
        findings.extend(_errors_to_findings(python_result.get("final_errors", []), "python", Severity.LOW))
        final_chunk = python_result.get("final_chunk")
        if isinstance(final_chunk, str) and final_chunk.strip():
            fixed_chunks.append(final_chunk)

    output_text = None
    if len(fixed_chunks) == 1:
        output_text = fixed_chunks[0]
    elif fixed_chunks:
        output_text = "\n\n".join(fixed_chunks)

    return AgentOutput(
        agent="lint-auditor",
        status="ok",
        findings=findings,
        output_text=output_text,
    )
