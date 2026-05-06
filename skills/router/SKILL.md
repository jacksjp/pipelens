---
name: router
description: Classify raw user input as sql_query, stored_procedure, or unknown. Use at the start of every Code Critic request before any analysis or data fetching begins.
---

## Inputs
- `user_input` — raw text submitted by the user

## Outputs
- `input_type` — `sql_query` | `stored_procedure` | `unknown`
- `confidence` — float 0–1
- `reasoning` — one-sentence justification
- `object_name` — fully-qualified identifier, only if stored_procedure. Must include parentheses, for example `DB.SCHEMA.PROC_NAME()`.

