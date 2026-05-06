"""Central prompt constants for Code Critic. Import from here everywhere."""

import pathlib

_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"


def _read_skill(name: str) -> str:
    return (_SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")


def _extract_between(text: str, start: str, end: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"Markers not found: {start!r}")
    return text.split(start, 1)[1].split(end, 1)[0].strip()


# ── Router ────────────────────────────────────────────────────────────────────
ROUTER_SKILL: str = _read_skill("router")

# ── Schema-fetcher ────────────────────────────────────────────────────────────
SCHEMA_FETCHER_SKILL: str = _read_skill("schema-fetcher")
SCHEMA_FETCHER_ETL_PROMPT: str = _extract_between(
    SCHEMA_FETCHER_SKILL, "<!-- ETL_PROMPT_START -->", "<!-- ETL_PROMPT_END -->"
)

# ── Analyzers & Synthesizer (stubs — loaded now so constants are ready) ───────
PERFORMANCE_ANALYZER_SKILL: str = _read_skill("performance-analyzer")
SECURITY_AUDITOR_SKILL: str = _read_skill("security-auditor")
STYLE_REVIEWER_SKILL: str = _read_skill("style-reviewer")
SYNTHESIZER_SKILL: str = _read_skill("synthesizer")
