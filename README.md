# PipeLens (W.I.P)

PipeLens is an agentic AI project focused on identifying and solving real-world issues in modern data pipelines across enterprise platforms such as Snowflake, Databricks, and BigQuery.


## Overview

The long-term goal is to build an assistant that reviews SQL, Python, Spark, and analytics engineering artifacts to detect production-grade issues before they become incidents. Over time, the platform is intended to include optimization and cost-impact analysis so teams can quantify expected savings from recommended changes.


## Current Scope (In Progress)

- Platform focus: enterprise data platforms
- Current input types by object family:
	- SQL-based objects: stored procedures, ad-hoc SQL queries, views, materialized views, UDFs, and DDL scripts
	- Python-based objects: Python stored procedures, Python UDF handlers
	- Spark-based objects: Spark SQL statements, PySpark DataFrame transformation pipelines, and Spark job/notebook code
- Analysis dimension currently implemented: linting-first workflow
- Output today: structured lint findings plus actionable rewrites and explanations

## Future State (Original Plan)

The same review workflow is intended to expand well beyond linting into a broader pipeline quality and optimization system.

- Notebooks
- dbt models
- SQLMesh models
- Orchestration models
- Performance diagnostics
- Security checks
- Cost-aware optimization recommendations


## Proposed Findings

The application returns a ranked `FindingsReport` with structured review output. Each finding is designed to include:

- Severity rating
- Plain-language description of the issue
- Original offending snippet
- Suggested rewritten code
- Line-by-line explanation of the change

The goal is to give data engineers and analytics engineers the same depth of review they would get from a senior peer, delivered automatically and consistently inside their existing data platform workflow.

## Agentic AI High-Level Flow

The active implementation currently uses a lint-focused path while the full multi-agent roadmap remains in scope.

```text
[User Input: SQL text]
         |
         v
    lint-auditor
         |
         v
   [FindingsReport]
```

## How It Works (Current)

1. The orchestrator receives code input from the frontend.
2. The lint-auditor validates and critiques code with lint-focused checks.
3. The orchestrator maps agent output into the shared FindingsReport response shape.

## Architecture Choices

- LangGraph: stateful orchestration, conditional routing, and parallel fan-out
- Configurable LLM providers: OpenAI, Anthropic, and Google model routing via agents.yaml
- Platform connectors: retrieval of DDL, query history, execution plans, and related metadata from connected enterprise data platforms
- Pydantic: output validation through the FindingsReport model
- Jupyter notebooks: required development format for the course project

## Memory Strategy (Planned)

The design keeps two memory layers:

- Short-term memory via LangGraph MemorySaver for follow-up questions in the same session
- Long-term memory via a local JSON history file so prior analyses can inform later runs

This allows the system to surface regressions and improvements when the same object is reviewed multiple times.

## Tool Use (Planned Extended Graph)

The schema-fetcher stage relies on two read-only retrieval tools:

- A source retrieval tool to fetch stored procedure DDL or recent ad-hoc query text
- An execution-plan retrieval tool to fetch a logical execution plan for SQL statements

Both tools run through read-only access patterns on the connected platform.

## Safeguards

The current design includes multiple guardrails:

- Read-only platform access to block DML and DDL execution
- Input validation for object names
- Output blocking for unsafe modification statements
- Pydantic validation for agent responses
- Secret detection before prompts are sent to the model

## Repository Layout

The codebase is a uv workspace (Python) plus a single npm package (frontend).

```
Project/
├── apps/
│   ├── orchestrator/   FastAPI orchestrator (single user-facing entry)
│   ├── mcp-server/     FastMCP server exposing shared tools
│   └── frontend/       Vite + React + TypeScript UI
├── agents/
│   ├── Dockerfile      Generic image, parameterized by AGENT_NAME / AGENT_MODULE
│   └── lint-auditor/
├── packages/
│   └── common/         Shared models (FindingsReport), prompts loader, agent runner
├── scripts/            lint / test / dev helpers (.sh and .ps1)
├── docker-compose.yml  Brings up the full stack
└── pyproject.toml      uv workspace root
```

## Setup

### 1. Install Python dependencies (uv workspace)

```bash
uv sync --all-packages
```

### 2. Install frontend dependencies (npm)

```bash
npm install --prefix apps/frontend
```

### 3. Configure environment

```bash
cp .env.example .env
# edit .env to add the keys for the providers you plan to use
```

## Running the Stack

### Without Docker (local dev)

```bash
# Linux / macOS
bash scripts/dev.sh

# Windows / PowerShell
scripts/dev.ps1
```

This starts the MCP server, the lint-auditor service, the orchestrator, and the Vite dev server.

- Frontend: http://localhost:5173
- Orchestrator: http://localhost:8000

Optional split scripts:

```bash
# Linux / macOS
bash scripts/run-backend.sh
bash scripts/run-frontend.sh

# Windows / PowerShell
scripts/run-backend.ps1
scripts/run-frontend.ps1
```

### With Docker (compose)

```bash
docker compose up --build
```

Same surface; orchestrator on host port 8000, frontend on host port 5173.

### Building a single agent image

The `agents/Dockerfile` is shared; the agent is selected by build args:

```bash
docker build -f agents/Dockerfile \
	--build-arg AGENT_NAME=lint-auditor \
	--build-arg AGENT_MODULE=agent_lint_auditor \
	-t code-critic/agent-lint-auditor .
```

## Tests and Linting

```bash
bash scripts/test.sh       # uv run pytest + npm test
bash scripts/lint.sh       # ruff + mypy + eslint + prettier
bash scripts/lint.sh --fix # auto-fix
```

## Status

PipeLens is still in active development. The current implementation is intentionally lint-first, while the broader original plan remains to expand into deeper multi-agent analysis across pipeline reliability, performance, security, and cost.

The notebook project description is still a design reference, and the implementation will continue to evolve as the capstone is built and tested.

## Author

Jayaprakash Sivanandam
