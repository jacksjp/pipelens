"""
PostToolUse hook — checks that every public function/class in a .py file has a docstring.
Exit 2 sends missing-docstring feedback to Claude so it adds them.
"""

import ast
import json
import sys
from pathlib import Path


def get_file_path(data: dict) -> str:
    """Extract the file path from hook input."""
    return data.get("tool_input", {}).get("file_path", "")


def find_missing_docstrings(source: str) -> list[str]:
    """Return qualified names of public functions/classes that lack docstrings."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []  # Let the linting hook handle syntax errors

    missing = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        # Skip private/dunder names
        if node.name.startswith("_"):
            continue
        # Check for docstring (first statement must be a string constant)
        has_docstring = (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )
        if not has_docstring:
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            missing.append(f"{kind} '{node.name}' (line {node.lineno})")

    return missing


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    file_path = get_file_path(data)

    if not file_path.endswith(".py"):
        return 0

    try:
        source = Path(file_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0

    missing = find_missing_docstrings(source)

    if missing:
        print(
            f"MISSING DOCSTRINGS in '{file_path}' — please add docstrings to:\n"
            + "\n".join(f"  - {item}" for item in missing),
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
