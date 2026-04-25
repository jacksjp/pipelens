"""
PostToolUse hook — runs flake8 on any .py file that was just written or edited.
Exit 2 sends linting errors back to Claude so it can fix the code.
"""

import json
import subprocess
import sys


def get_file_path(data: dict) -> str:
    """Extract the file path from hook input."""
    return data.get("tool_input", {}).get("file_path", "")


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    file_path = get_file_path(data)

    if not file_path.endswith(".py"):
        return 0

    result = subprocess.run(
        ["flake8", "--max-line-length=100", file_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(
            f"LINTING ERRORS in '{file_path}' — please fix before proceeding:\n{result.stdout}",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
