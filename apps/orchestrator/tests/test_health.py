"""Smoke tests for the orchestrator HTTP surface."""

from common import Finding, FindingsReport, Severity
from fastapi.testclient import TestClient
from orchestrator import main as orchestrator_main

client = TestClient(orchestrator_main.app)


def test_health_returns_ok() -> None:
    """/health responds 200 with a simple status payload."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_critique_returns_lint_report(monkeypatch: object) -> None:
    """/critique returns mapped output from the lint orchestrator flow."""

    def fake_run_lint(input_text: str) -> FindingsReport:
        assert input_text == "select 1"
        return FindingsReport(
            status="ok",
            agent="lint-auditor",
            findings=[
                Finding(
                    severity=Severity.LOW,
                    description="Issue [sql] LT01: spacing",
                    original_snippet="sql line 1:1",
                    suggested_fix=None,
                )
            ],
            improved_code="SELECT 1;",
        )

    monkeypatch.setattr(orchestrator_main, "run_lint", fake_run_lint)

    res = client.post("/critique", json={"input": "select 1"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["agent"] == "lint-auditor"
    assert len(body["findings"]) == 1
    assert body["improved_code"] == "SELECT 1;"
