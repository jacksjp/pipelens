---
name: synthesizer
description: Merge, deduplicate, and rank findings from all three analyzer nodes into a final FindingsReport. Use only after performance-analyzer, security-auditor, and style-reviewer have all completed.
---

## Inputs
- `performance_findings` — findings from performance-analyzer
- `security_findings` — findings from security-auditor
- `style_findings` — findings from style-reviewer
- `sql_text` — original SQL for context

## Outputs
- `report` — ranked `FindingsReport` with rewritten code and cost comparison

## Tools
TBD
