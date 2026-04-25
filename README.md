# Pipelens (W.I.P)

Piplens is a project focused on identifying and solving real-world issues in modern data pipelines across enterprise platforms like Snowflake, Databricks, and BigQuery.


## Overview

This project builds an agentic AI assistant that analyzes SQL and pipeline logic to detect production-grade issues before they become incidents. It also provides an estimated cost comparison before and after optimization so teams can quantify expected savings from the recommended changes.


## Current Scope

- Platform focus: enterprise data platforms
- Current input types by object family:
	- SQL-based objects: stored procedures, ad-hoc SQL queries, views, materialized views, UDFs, and DDL scripts
	- Python-based objects: Python stored procedures, Python UDF handlers
	- Spark-based objects: Spark SQL statements, PySpark DataFrame transformation pipelines, and Spark job/notebook code
- Analysis dimensions: performance, security, and style
- Output: structured findings plus rewritten code with explanations

## Future State

The same review workflow is intended to expand to additional analytics engineering artifacts.

- Notebooks
- dbt models
- SQLMesh models
- Orcehstration models


## Proposed Findings

The application returns a ranked `FindingsReport` with structured review output. Each finding is designed to include:

- Severity rating
- Plain-language description of the issue
- Original offending snippet
- Suggested rewritten code
- Line-by-line explanation of the change

The goal is to give data engineers and analytics engineers the same depth of review they would get from a senior peer, delivered automatically and consistently inside their existing data platform workflow.

## Agentic AI High-Level Flow

The application uses a LangGraph `StateGraph` with specialized nodes connected through a shared `AgentState`.

```text
[User Input: object name or SQL text]
	      |
	      v
	   router
	   |     |
	(SP path) (query path)
	   |     |
	   v     v
	schema_fetcher
	      |
	      v
	+-------+--------+--------+
	|                |        |
	v                v        v
performance_   security_  style_
analyzer       auditor    reviewer
	|                |        |
	+-------+--------+--------+
	      |
	      v
	  synthesizer
	      |
	      v
	[FindingsReport]
```

## How It Works

1. The `router` classifies the input and decides whether the flow should use the stored procedure path or the ad-hoc query path.
2. The `schema_fetcher` retrieves SQL text and execution context from the connected platform using read-only retrieval tools.
3. The `performance_analyzer`, `security_auditor`, and `style_reviewer` run in parallel.
4. The `synthesizer` merges, ranks, and formats the final findings.

## Architecture Choices

- LangGraph: stateful orchestration, conditional routing, and parallel fan-out
- Google Gemini: strong code understanding with structured JSON output support
- Platform connectors: retrieval of DDL, query history, execution plans, and related metadata from connected enterprise data platforms
- Pydantic: output validation through the `FindingsReport` model
- Jupyter notebooks: required development format for the course project

## Memory Strategy

The design uses two memory layers:

- Short-term memory via LangGraph `MemorySaver` for follow-up questions in the same session
- Long-term memory via a local JSON history file so prior analyses can inform later runs

This allows the system to surface regressions and improvements when the same object is reviewed multiple times.

## Tool Use

The `schema_fetcher` node relies on two read-only retrieval tools:

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

## Setup

### 1. Activate virtual environment

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Repository Files

- AGENTS.md
- PROJECT_DESCRIPTION.ipynb
- README.md
- requirements.txt

## Status

Piplens is still in active development. The notebook project description is the current design reference, and the implementation will evolve as the capstone is built and tested.

## Author

Jayaprakash Sivanandam
