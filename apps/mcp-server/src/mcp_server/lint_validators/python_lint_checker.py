"""Python lint/fix helpers for MCP tools."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _error_sig(err: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    return (
        err.get("line_no"),
        err.get("line_pos"),
        err.get("code"),
        err.get("description"),
    )


def lint_ruff_errors(python_text: str) -> list[dict[str, Any]]:
    """Return normalized Ruff lint violations for a Python snippet."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_file = Path(tmp_dir) / "snippet.py"
        temp_file.write_text(python_text, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                str(temp_file),
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode not in (0, 1):
            raise RuntimeError(
                "Ruff lint failed: " + (result.stderr.strip() or result.stdout.strip())
            )

        raw_items = json.loads(result.stdout or "[]")
        return [
            {
                "line_no": item.get("location", {}).get("row"),
                "line_pos": item.get("location", {}).get("column"),
                "code": item.get("code"),
                "description": item.get("message"),
            }
            for item in raw_items
        ]


def fix_ruff_errors(python_text: str) -> str:
    """Return Python text after Ruff auto-fixes are applied."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_file = Path(tmp_dir) / "snippet.py"
        temp_file.write_text(python_text, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                str(temp_file),
                "--fix",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode not in (0, 1):
            raise RuntimeError(
                "Ruff fix failed: " + (result.stderr.strip() or result.stdout.strip())
            )

        return temp_file.read_text(encoding="utf-8")


def lint_fix_python(python_text: str) -> dict[str, Any]:
    """Run lint-fix-lint flow and return a consistent state payload."""
    initial_errors = lint_ruff_errors(python_text)
    final_chunk = fix_ruff_errors(python_text)
    final_errors = lint_ruff_errors(final_chunk)

    initial_by_sig = {_error_sig(err): err for err in initial_errors}
    final_sigs = {_error_sig(err) for err in final_errors}
    fixed_errors = [initial_by_sig[sig] for sig in initial_by_sig if sig not in final_sigs]

    return {
        "initial_errors": initial_errors,
        "fixed_errors": fixed_errors,
        "final_chunk": final_chunk,
        "final_errors": final_errors,
    }
