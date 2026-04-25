# Piplens

Piplens is an ongoing project focused on identifying and solving real-world issues in modern data pipelines across enterprise platforms like Snowflake, Databricks, and BigQuery.

## Project Name Ideas

- Pipeline Pulse
- DataFlow Sentinel
- Warehouse Watchtower
- QueryGuard AI
- PipeLens
- DataOps Code Critic
- Pipeline Reliability Lab

## Overview

This project builds an agentic AI assistant that analyzes SQL and pipeline logic to detect production-grade issues before they become incidents.

Core outputs:

1. Findings report (performance, correctness, reliability, style, security)
2. Improved code recommendations with explanation of every suggested change

The main goal is to make data teams faster, safer, and more consistent when working with complex analytics pipelines.

## Why This Project

Real-world data systems often fail due to avoidable problems such as:

- Inefficient SQL patterns that increase compute cost
- Fragile transformations that break on schema drift
- Incorrect join/filter logic that introduces data quality issues
- Missing safeguards around permissions, secrets, and environment separation
- Inconsistent coding standards across teams and platforms

This project aims to detect these problems early and provide practical fixes.

## Scope

Current and target service coverage:

- Snowflake
- Databricks (SQL + Spark SQL contexts)
- BigQuery

Input types:

- Ad-hoc SQL queries
- Stored procedures
- Pipeline transformation logic (incremental models, staging-to-curated patterns)

## High-Level Approach

The system follows an agentic analysis loop:

1. Intake and classify query/procedure/pipeline artifact
2. Retrieve execution and metadata context when available
3. Run specialized analyzers in parallel (performance, correctness, security, style)
4. Merge and rank findings by severity and impact
5. Generate revised SQL and implementation guidance

## Design Principles

- Keep recommendations practical and production-oriented
- Prefer explainable fixes over opaque rewrites
- Enforce read-only analysis paths for connected systems
- Keep implementation DRY and simple
- Use structured output models for deterministic reporting

## Proposed Findings Format

Each finding is expected to include:

- Severity (Critical, High, Medium, Low)
- Issue category (performance, correctness, reliability, style, security)
- Affected snippet
- Why it matters in production
- Suggested fix
- Confidence level

## Repository Snapshot

Current workspace files:

- AGENTS.md
- PROJECT_DESCRIPTION.ipynb
- README.md
- requirements.txt

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

## Roadmap

- Baseline analyzer for SQL anti-pattern detection
- Platform-aware rule packs for Snowflake, Databricks, and BigQuery
- Structured findings schema and scoring model
- Improved rewrite engine with side-by-side diff output
- Benchmark suite with real incident-inspired test cases

## Status

This project is actively in progress. Architecture, analyzer depth, and platform coverage will continue to evolve as real use cases are validated.

## Author

Jayaprakash Sivanandam

## Disclaimer

Piplens is still in active development and is not MVP-ready yet. Features, architecture, and platform support are evolving and may change.
