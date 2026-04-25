"""
PreToolUse hook — blocks Write/Edit if the content contains secrets.
Exit 2 causes Claude Code to cancel the tool call entirely.
"""

import json
import re
import sys

# Patterns that indicate a hard-coded secret.
# Each entry is (label, compiled_regex).
SECRET_PATTERNS = [
    ("Anthropic API key", re.compile(r"sk-ant-[a-zA-Z0-9\-_]{20,}")),
    ("OpenAI API key", re.compile(r"sk-[a-zA-Z0-9]{32,}")),
    ("AWS access key", re.compile(r"AKIA[A-Z0-9]{16}")),
    ("AWS secret key assignment", re.compile(r'(?i)(aws_secret_access_key\s*=\s*)["\']?[A-Za-z0-9/+=]{40}')),
    ("Private key block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("Generic API key assignment", re.compile(r'(?i)(api_key|apikey)\s*=\s*["\'](?!your_|<|{|\s*$)[^"\']{8,}')),
    ("Generic password assignment", re.compile(r'(?i)(password|passwd|pwd)\s*=\s*["\'](?!your_|<|{|\s*$)[^"\']{4,}')),
    ("Generic secret assignment", re.compile(r'(?i)(secret|token)\s*=\s*["\'](?!your_|<|{|\s*$)[^"\']{8,}')),
    ("Credentials in URL", re.compile(r"[a-zA-Z]+://[^:@\s]+:[^@\s]{4,}@")),
]

# Files where secret-like content is expected and should be allowed.
SAFE_FILENAME_SUFFIXES = (
    ".env.example",
    ".env.template",
    ".env.sample",
    "check_secrets.py",  # this file itself
)


def get_content_and_path(data: dict) -> tuple[str, str]:
    """Extract the text being written and its destination path from hook input."""
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    # Write tool uses 'content'; Edit tool uses 'new_string'
    content = tool_input.get("content") or tool_input.get("new_string") or ""
    return content, file_path


def is_safe_file(file_path: str) -> bool:
    """Return True for files that are allowed to contain placeholder secrets."""
    lower = file_path.lower().replace("\\", "/")
    return any(lower.endswith(suffix) for suffix in SAFE_FILENAME_SUFFIXES)


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0  # Can't parse input — don't block

    content, file_path = get_content_and_path(data)

    if is_safe_file(file_path):
        return 0

    found = []
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(content):
            found.append(label)

    if found:
        print(
            f"SECRET DETECTED — write blocked.\n"
            f"Found potential secret(s) in '{file_path}':\n"
            + "\n".join(f"  - {label}" for label in found)
            + "\n\nMove secrets to the .env file and reference them via os.environ or python-dotenv.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
