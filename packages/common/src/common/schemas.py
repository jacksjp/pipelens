"""Shared pydantic models exchanged between agents and the orchestrator."""

from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    """Severity level attached to a single finding."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    """One issue identified by an analyzer agent."""

    severity: Severity
    description: str
    original_snippet: str | None = None
    suggested_fix: str | None = None


class AgentInput(BaseModel):
    """Envelope for input passed into an agent's executor."""

    text: str
    metadata: dict[str, str] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Envelope returned from an agent's executor."""

    agent: str
    status: str = "ok"
    findings: list[Finding] = Field(default_factory=list)
    output_text: str | None = None


class FindingsReport(BaseModel):
    """Final synthesized report returned by the orchestrator."""

    status: str = "ok"
    agent: str
    findings: list[Finding] = Field(default_factory=list)
    improved_code: str | None = None
