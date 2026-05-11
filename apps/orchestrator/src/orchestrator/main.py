"""FastAPI orchestrator entry point for the Code Critic system."""

from common import FindingsReport
from fastapi import FastAPI
from pydantic import BaseModel

from orchestrator.graph import run_lint

app = FastAPI(title="Code Critic Orchestrator", version="0.1.0")


class CritiqueRequest(BaseModel):
    """Body schema for POST /critique."""

    input: str


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker / compose health checks."""
    return {"status": "ok"}


@app.post("/critique")
def critique(req: CritiqueRequest) -> FindingsReport:
    """Run lint analysis through the lint-auditor and return findings."""
    return run_lint(req.input)
