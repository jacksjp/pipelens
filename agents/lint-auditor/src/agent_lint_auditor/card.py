"""Agent card metadata used for discovery."""

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

LINT_SKILL = AgentSkill(
    id="lint-auditor",
    name="Lint & Auto-Fix Code",
    description=(
        "Lint and auto-fix SQL and Python code, including mixed embedded SQL snippets. "
        "Detects formatting issues, code style violations, and quality problems using "
        "SQLFluff (SQL) and Ruff (Python). Returns severity-categorized findings and "
        "auto-fixed code."
    ),
    tags=["linting", "sql", "python", "code-quality", "auto-fix"],
    input_modes=["text"],
    output_modes=["text"],
)

CARD = AgentCard(
    name="lint-auditor",
    version="0.1.0",
    description="Lint SQL and Python code, including mixed embedded SQL snippets.",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[LINT_SKILL],
)
