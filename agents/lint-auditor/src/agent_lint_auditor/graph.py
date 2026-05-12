"""LangGraph workflow for SQL and Python linting via MCP tool calling."""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
from typing import Any, Literal, TypedDict, cast

from fastmcp import Client
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


class LintFixState(TypedDict, total=False):
    """State for the lint-fix workflow."""

    code: str
    language: Literal["python", "sql", "mixed", "unknown"]
    llm: BaseChatModel
    mcp_url: str
    messages: list[BaseMessage]
    tool_results: list[dict[str, Any]]
    parsed_blocks: list[dict[str, Any]]
    # Populated from MCP tool responses
    initial_errors: list[dict[str, Any]]
    fixed_errors: list[dict[str, Any]]
    remaining_errors: list[dict[str, Any]]
    fixed_code: str
    # Final output
    fix_report: list[dict[str, Any]]
    final_code: str
    max_retries: int


# ===== Pydantic models for structured LLM output =====


class LanguageDetectionResult(BaseModel):
    """Result of language detection by LLM."""

    language: Literal["python", "sql", "mixed", "unknown"] = Field(
        description="Detected language(s) in the code"
    )
    reasoning: str = Field(description="Brief reasoning for the detection")


class FixExplanation(BaseModel):
    """Explanation for a single lint fix."""

    rule_code: str = Field(description="Lint rule code, e.g. E501, L003, AM04")
    original_error: str = Field(description="Original error description as reported by the linter")
    fix_applied: str = Field(
        description="What was changed in the code to fix this error. Empty string if fixable=false."
    )
    explanation: str = Field(
        default="",
        description="Why this fix is correct — the rule, style guide, or best practice it enforces",
    )
    fixable: bool = Field(
        default=True,
        description=(
            "False when the fix requires information not available in the code itself, "
            "e.g. actual column names for SELECT *, table schema, runtime values. "
            "When false, fix_applied must be empty and the original code must be left unchanged."
        ),
    )
    cannot_fix_reason: str = Field(
        default="",
        description="Human-readable reason why this issue cannot be auto-fixed. Required when fixable=false.",
    )


class LintReport(BaseModel):
    """Full lint report returned by the LLM after reviewing MCP tool results."""

    fixed_explanations: list[FixExplanation] = Field(
        description="Explanation for each error that was auto-fixed by the lint tool"
    )
    remaining_explanations: list[FixExplanation] = Field(
        default_factory=list,
        description=(
            "Assessment of errors still remaining after tool auto-fix. "
            "Set fixable=false for any error that requires schema knowledge or external context "
            "(e.g. SELECT *, unknown column names, missing table definitions)."
        ),
    )
    llm_fixed_code: str = Field(
        description=(
            "Final corrected code. For fixable=false errors, leave the original code unchanged — "
            "do NOT invent column names, table structures, or any other schema-dependent content."
        )
    )
    summary: str = Field(description="Brief overall summary of what was found and fixed")


class CodeBlock(BaseModel):
    """A single ordered segment from the original mixed-language source."""

    index: int = Field(description="0-based order index of this segment in the source")
    language: Literal["python", "sql", "other"] = Field(description="Language for this segment")
    content: str = Field(description="Exact segment text from the original source")


class CodeBlocksResult(BaseModel):
    """Ordered partition of source code into lintable and passthrough segments."""

    blocks: list[CodeBlock] = Field(description="Ordered list of source segments")


# ===== MCP tool helpers =====


def _run_async(coro: Any) -> Any:
    """Run an async coroutine safely from a synchronous context."""
    try:
        asyncio.get_running_loop()
        # Already inside a running loop — delegate to a thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    except RuntimeError:
        return asyncio.run(coro)


async def _call_mcp_tool(url: str, tool_name: str, arguments: dict[str, Any]) -> Any:
    """Invoke a single MCP tool and return parsed JSON result.

    fastmcp's Client.call_tool() returns a CallToolResult object.
    Its .content attribute is the list of TextContent / other content items.
    """
    async with Client(url) as client:
        result = await client.call_tool(tool_name, arguments)

    # Unwrap CallToolResult -> content list
    content = getattr(result, "content", None)
    if content is None:
        # Fallback: some versions expose items directly as iterable
        try:
            content = list(result)
        except TypeError:
            return result

    if not content:
        return {}

    first = content[0]
    text = getattr(first, "text", None)
    if text is not None:
        try:
            return json.loads(text)
        except json.JSONDecodeError, ValueError:
            return text
    return first


# ===== Graph nodes =====


def detect_language_node(state: LintFixState) -> LintFixState:
    """Use LLM to detect whether the code is Python, SQL, mixed, or unknown."""
    llm = state["llm"]
    code = state["code"]

    prompt = (
        "Analyze the following code and detect its language(s).\n\n"
        f"Code:\n{code}\n\n"
        "Classify the code using ONLY one of these values:\n"
        "  - 'python'  : the code is Python (including Jupyter-style cells)\n"
        "  - 'sql'     : the code is SQL (any dialect)\n"
        "  - 'mixed'   : the code contains both Python and SQL\n"
        "  - 'unknown' : the code is ANY other language (shell, bash, PowerShell, "
        "JavaScript, TypeScript, Rust, Go, YAML, etc.) OR the language cannot be determined.\n\n"
        "IMPORTANT: If the code is a shell script, PowerShell script, batch file, "
        "or any language other than Python or SQL, you MUST return 'unknown'.\n"
        "Return your answer as JSON matching LanguageDetectionResult."
    )

    result_raw = llm.with_structured_output(LanguageDetectionResult).invoke(prompt)
    if isinstance(result_raw, LanguageDetectionResult):
        result = result_raw
    else:
        result = LanguageDetectionResult.model_validate(result_raw)
    return {"language": result.language}


def call_lint_tools_node(state: LintFixState) -> LintFixState:
    """Use LLM block extraction, then lint each block with the appropriate tool."""
    llm = state["llm"]
    code = state["code"]
    language = state.get("language", "unknown")
    mcp_url = state["mcp_url"]

    tool_results: list[dict[str, Any]] = []
    parsed_blocks: list[dict[str, Any]] = []

    if language == "mixed":
        prompt = (
            "You are a precise code segmenter. Partition the source into ordered, non-overlapping "
            "blocks so the concatenation of all block content is EXACTLY the original input.\n\n"
            "Rules:\n"
            "1. Return ONLY JSON matching CodeBlocksResult.\n"
            "2. Every character from the input must appear in exactly one block content.\n"
            "3. Preserve original whitespace, indentation, delimiters, and comments exactly.\n"
            "4. Set language='python' for Python code regions, language='sql' for SQL regions, "
            "and language='other' for wrappers/metadata/non-lintable separators.\n"
            "5. index values must be 0..N-1 in order.\n\n"
            f"SOURCE:\n{code}"
        )
        block_raw = llm.with_structured_output(CodeBlocksResult).invoke(prompt)
        if isinstance(block_raw, CodeBlocksResult):
            block_result = block_raw
        else:
            block_result = CodeBlocksResult.model_validate(block_raw)
        parsed_blocks = [block.model_dump() for block in block_result.blocks]
    else:
        normalized = "python" if language == "python" else "sql"
        parsed_blocks = [{"index": 0, "language": normalized, "content": code}]

    for block in parsed_blocks:
        block_index = int(block.get("index", 0))
        block_language = str(block.get("language", "other"))
        block_content = str(block.get("content", ""))

        if not block_content.strip() or block_language == "other":
            continue

        if block_language == "python":
            python_result = _run_async(
                _call_mcp_tool(mcp_url, "lint_fix_python", {"python_text": block_content})
            )
            tool_results.append(
                {"tool": "lint_fix_python", "block_index": block_index, "result": python_result}
            )
        elif block_language == "sql":
            sql_result = _run_async(
                _call_mcp_tool(
                    mcp_url,
                    "lint_fix_sql",
                    {"sql_text": block_content, "user_dialect": "snowflake"},
                )
            )
            tool_results.append(
                {"tool": "lint_fix_sql", "block_index": block_index, "result": sql_result}
            )

    return {"tool_results": tool_results, "parsed_blocks": parsed_blocks, "messages": []}


def execute_tools_node(state: LintFixState) -> LintFixState:
    """No-op node retained for backward compatibility in graph wiring."""
    return state


def process_results_node(state: LintFixState) -> LintFixState:
    """Merge ToolMessage payloads from MCP into structured state fields."""
    messages = state.get("messages", [])
    tool_results = state.get("tool_results", [])
    parsed_blocks = state.get("parsed_blocks", [])

    initial_errors: list[dict[str, Any]] = []
    fixed_errors: list[dict[str, Any]] = []
    remaining_errors: list[dict[str, Any]] = []
    fixed_code_parts: list[str] = []

    for msg in messages:
        if isinstance(msg, ToolMessage):
            try:
                if isinstance(msg.content, str):
                    parsed_content = json.loads(msg.content)
                else:
                    parsed_content = msg.content

                if not isinstance(parsed_content, dict):
                    continue

                data: dict[str, Any] = parsed_content
                if isinstance(data, dict):
                    initial_errors.extend(data.get("initial_errors", []))
                    fixed_errors.extend(data.get("fixed_errors", []))
                    remaining_errors.extend(data.get("final_errors", []))
                    chunk = data.get("final_chunk", "")
                    if chunk:
                        fixed_code_parts.append(chunk)
            except json.JSONDecodeError, TypeError:
                pass

    for entry in tool_results:
        data = entry.get("result", {})
        if isinstance(data, dict):
            initial_errors.extend(data.get("initial_errors", []))
            fixed_errors.extend(data.get("fixed_errors", []))
            remaining_errors.extend(data.get("final_errors", []))

    if parsed_blocks:
        rebuilt_blocks: list[str] = [str(block.get("content", "")) for block in parsed_blocks]
        for entry in tool_results:
            data = entry.get("result", {})
            chunk = data.get("final_chunk", "") if isinstance(data, dict) else ""
            block_index = entry.get("block_index")
            if (
                isinstance(chunk, str)
                and chunk
                and isinstance(block_index, int)
                and 0 <= block_index < len(rebuilt_blocks)
            ):
                rebuilt_blocks[block_index] = chunk
        fixed_code = "".join(rebuilt_blocks)
    else:
        for entry in tool_results:
            data = entry.get("result", {})
            chunk = data.get("final_chunk", "") if isinstance(data, dict) else ""
            if chunk:
                fixed_code_parts.append(chunk)
        fixed_code = "\n\n".join(fixed_code_parts) if fixed_code_parts else state["code"]

    return {
        "initial_errors": initial_errors,
        "fixed_errors": fixed_errors,
        "remaining_errors": remaining_errors,
        "fixed_code": fixed_code,
    }


def llm_explain_node(state: LintFixState) -> LintFixState:
    """LLM reviews tool results and produces per-fix explanations + attempts remaining fixes."""
    llm = state["llm"]
    code = state["code"]
    fixed_code = state.get("fixed_code", code)
    initial_errors = state.get("initial_errors", [])
    fixed_errors = state.get("fixed_errors", [])
    remaining_errors = state.get("remaining_errors", [])

    def _fmt(errors: list[dict[str, Any]]) -> str:
        if not errors:
            return "  (none)"
        return "\n".join(
            f"  - Line {e.get('line_no', '?')}:{e.get('line_pos', '?')} "
            f"[{e.get('code', '?')}] {e.get('description', '')}"
            for e in errors
        )

    prompt = (
        "You are a code quality expert. Review the linting results below and produce a detailed report.\n\n"
        f"=== ORIGINAL CODE ===\n{code}\n\n"
        f"=== AUTO-FIXED CODE (after MCP tool fixes) ===\n{fixed_code}\n\n"
        f"=== INITIAL ERRORS FOUND ({len(initial_errors)}) ===\n{_fmt(initial_errors)}\n\n"
        f"=== ERRORS AUTO-FIXED BY TOOLS ({len(fixed_errors)}) ===\n{_fmt(fixed_errors)}\n\n"
        f"=== ERRORS STILL REMAINING ({len(remaining_errors)}) ===\n{_fmt(remaining_errors)}\n\n"
        "INSTRUCTIONS:\n"
        "1. For each AUTO-FIXED error: explain what changed and WHY (reference the lint rule).\n"
        "2. For each REMAINING error:\n"
        "   a. If the fix requires information NOT present in the code (e.g. actual column names for\n"
        "      SELECT *, table schema, runtime values, external configuration) — set fixable=false,\n"
        "      leave fix_applied empty, populate cannot_fix_reason with a clear explanation,\n"
        "      and DO NOT change that part of the code in llm_fixed_code.\n"
        "   b. If the fix can be determined from the code alone — set fixable=true and apply it.\n"
        "3. llm_fixed_code must be the tool-fixed code with only fixable=true changes applied on top.\n"
        "   Never invent column names, table structures, or any schema-dependent content.\n"
        "Return your response as JSON matching LintReport."
    )

    report_raw = llm.with_structured_output(LintReport).invoke(prompt)
    if isinstance(report_raw, LintReport):
        report = report_raw
    else:
        report = LintReport.model_validate(report_raw)

    # Be defensive against partial structured outputs where explanation can be empty.
    for entry in report.fixed_explanations:
        if not entry.explanation:
            entry.explanation = "Applied lint rule compliant change."

    for entry in report.remaining_explanations:
        if not entry.explanation:
            if entry.fixable:
                entry.explanation = "Resolvable from local code context; fix can be applied safely."
            else:
                entry.explanation = (
                    entry.cannot_fix_reason
                    or "Requires external context not present in the provided code."
                )

    fix_report = [
        {
            "rule_code": f.rule_code,
            "original_error": f.original_error,
            "fix_applied": f.fix_applied,
            "explanation": f.explanation,
            "fixable": True,
            "cannot_fix_reason": "",
            "category": "auto-fixed",
        }
        for f in report.fixed_explanations
    ] + [
        {
            "rule_code": f.rule_code,
            "original_error": f.original_error,
            "fix_applied": f.fix_applied,
            "explanation": f.explanation,
            "fixable": f.fixable,
            "cannot_fix_reason": f.cannot_fix_reason,
            "category": "llm-fixed" if f.fixable else "unfixable",
        }
        for f in report.remaining_explanations
    ]

    return {
        "fix_report": fix_report,
        "final_code": report.llm_fixed_code,
    }


def unknown_language_node(state: LintFixState) -> LintFixState:
    """Early-exit node when language cannot be identified."""
    return {
        "fix_report": [
            {
                "rule_code": "LANG",
                "original_error": "Language could not be identified.",
                "fix_applied": "",
                "explanation": (
                    "The submitted code could not be identified as Python, SQL, or a mix of both. "
                    "Please ensure the input contains valid Python or SQL code."
                ),
                "fixable": False,
                "cannot_fix_reason": (
                    "Unable to identify the programming language. No linting or fixes were applied."
                ),
                "category": "unfixable",
            }
        ],
        "final_code": state["code"],
    }


# ===== Conditional edges =====


def _route_after_detect(state: LintFixState) -> str:
    """Skip linting entirely when the language is unknown."""
    return "unknown" if state.get("language") == "unknown" else "call_lint_tools"


def _has_tool_calls(state: LintFixState) -> str:
    """Route to tool execution if the LLM produced tool calls, otherwise skip ahead."""
    if state.get("tool_results"):
        return "process_results"

    messages = state.get("messages", [])
    last = messages[-1] if messages else None
    if isinstance(last, AIMessage) and last.tool_calls:
        return "execute_tools"
    return "process_results"


# ===== Graph builder =====


def build_lint_fix_graph() -> Any:
    """Build and compile the LangGraph lint-fix workflow."""
    graph = StateGraph(LintFixState)

    graph.add_node("detect_language", detect_language_node)
    graph.add_node("unknown_language", unknown_language_node)
    graph.add_node("call_lint_tools", call_lint_tools_node)
    graph.add_node("execute_tools", execute_tools_node)
    graph.add_node("process_results", process_results_node)
    graph.add_node("llm_explain", llm_explain_node)

    graph.add_edge(START, "detect_language")
    graph.add_conditional_edges(
        "detect_language",
        _route_after_detect,
        {"call_lint_tools": "call_lint_tools", "unknown": "unknown_language"},
    )
    graph.add_edge("unknown_language", END)
    graph.add_conditional_edges(
        "call_lint_tools",
        _has_tool_calls,
        {"execute_tools": "execute_tools", "process_results": "process_results"},
    )
    graph.add_edge("execute_tools", "process_results")
    graph.add_edge("process_results", "llm_explain")
    graph.add_edge("llm_explain", END)

    return graph.compile()


def run_lint_fix_graph(
    code: str,
    llm: BaseChatModel,
    mcp_url: str,
    max_retries: int = 3,
) -> LintFixState:
    """
    Run the lint-fix workflow.

    Args:
        code: Code to lint and fix.
        llm: LangChain LLM instance.
        mcp_url: URL of the MCP server (e.g. "http://127.0.0.1:9000/mcp").
        max_retries: Kept for API compatibility; not used in the tool-calling flow.

    Returns:
        Final state containing initial_errors, fixed_errors, remaining_errors,
        fix_report, final_code.
    """
    app = build_lint_fix_graph()

    initial_state: LintFixState = {
        "code": code,
        "llm": llm,
        "mcp_url": mcp_url,
        "language": "unknown",
        "messages": [],
        "tool_results": [],
        "parsed_blocks": [],
        "initial_errors": [],
        "fixed_errors": [],
        "remaining_errors": [],
        "fixed_code": code,
        "fix_report": [],
        "final_code": code,
        "max_retries": max_retries,
    }

    return cast(LintFixState, app.invoke(initial_state))
