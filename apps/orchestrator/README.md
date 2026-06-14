# orchestrator

FastAPI service that fronts the Pipelens agent graph for the React UI.

## Endpoints

- `GET /health` — liveness probe.
- `POST /critique` — body `{ "input": "<sql or proc name>" }` → `FindingsReport`.
- `GET /agents` — lists configured agent base URLs from environment.

## Run locally

```bash
uv run --package orchestrator uvicorn orchestrator.main:app --reload --port 8000
```
