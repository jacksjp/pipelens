"""
PostToolUse hook — runs black on any .py file that was just written or edited.
Auto-formats in place silently. Always exits 0 (non-blocking).
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
        ["black", "--line-length=100", "--quiet", file_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Log the failure but don't block — formatting errors are non-critical
        print(f"black could not format '{file_path}': {result.stderr}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
