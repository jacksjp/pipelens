---
name: security-auditor
description: Flag security vulnerabilities in SQL queries and stored procedures. Use in parallel with performance-analyzer and style-reviewer once sql_text is available.
---

## Inputs
- `sql_text` — SQL query or stored procedure body

## Outputs
- `findings` — list of findings, each with `severity`, `description`, `snippet`, `suggestion`

## Tools
TBD
