---
name: style-reviewer
description: Catch style and readability violations in SQL queries and stored procedures. Use in parallel with performance-analyzer and security-auditor once sql_text is available.
---

## Inputs
- `sql_text` — SQL query or stored procedure body

## Outputs
- `findings` — list of findings, each with `severity`, `description`, `snippet`, `suggestion`

## Tools
TBD
