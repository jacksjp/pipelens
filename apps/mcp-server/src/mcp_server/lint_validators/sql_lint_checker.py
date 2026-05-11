"""SQL lint/fix helpers for MCP tools."""

from typing import Any

from sqlfluff.api import simple as sqlfluff

SUPPORTED_DIALECTS = {"snowflake", "databricks", "postgres", "bigquery", "duckdb"}


def _normalize_dialect(user_dialect: str | None) -> str:
    chosen = (user_dialect or "").strip().lower()
    return chosen if chosen in SUPPORTED_DIALECTS else "snowflake"


def _error_sig(err: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    return (
        err.get("line_no"),
        err.get("line_pos"),
        err.get("code"),
        err.get("description"),
    )


def lint_sqlfluff_errors(sql_text: str, user_dialect: str | None = None) -> list[dict[str, Any]]:
    """Return normalized SQLFluff lint violations for the provided SQL."""
    dialect = _normalize_dialect(user_dialect)
    violations = sqlfluff.lint(sql_text, dialect=dialect)
    return [
        {
            "line_no": item.get("start_line_no"),
            "line_pos": item.get("start_line_pos"),
            "code": item.get("code"),
            "description": item.get("description"),
        }
        for item in violations
    ]


def fix_sqlfluff_errors(sql_text: str, user_dialect: str | None = None) -> str:
    """Return SQL after SQLFluff auto-fixes are applied."""
    dialect = _normalize_dialect(user_dialect)
    violations = sqlfluff.lint(sql_text, dialect=dialect)
    if not violations:
        return sql_text
    return sqlfluff.fix(sql_text, dialect=dialect)


def lint_fix_sql(sql_text: str, user_dialect: str | None = None) -> dict[str, Any]:
    """Run lint-fix-lint flow and return a consistent state payload."""
    initial_errors = lint_sqlfluff_errors(sql_text, user_dialect=user_dialect)
    final_chunk = fix_sqlfluff_errors(sql_text, user_dialect=user_dialect)
    final_errors = lint_sqlfluff_errors(final_chunk, user_dialect=user_dialect)

    initial_by_sig = {_error_sig(err): err for err in initial_errors}
    final_sigs = {_error_sig(err) for err in final_errors}
    fixed_errors = [initial_by_sig[sig] for sig in initial_by_sig if sig not in final_sigs]

    return {
        "initial_errors": initial_errors,
        "fixed_errors": fixed_errors,
        "final_chunk": final_chunk,
        "final_errors": final_errors,
    }
