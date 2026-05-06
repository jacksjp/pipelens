---
name: schema-fetcher
description: Retrieve DDL or query text from Snowflake for a stored procedure or other named object. Use after the router classifies input as stored_procedure and before any analyzer node runs.
compatibility: Requires Python 3.10+, snowflake-snowpark-python, keyring. Needs Snowflake network access and a CODE_CRITIC_RO role. Connection params read from config.ini; password from Windows Credential Manager.
---

## Role
You are the schema-fetcher node. Your job is to retrieve DDL text for a named Snowflake object using the Snowflake tool, then extract only executable ETL code using the LLM-based extractor. Do not perform critique or scoring.

## Inputs
- `object_name` — stored procedure identifier from upstream router input
	- Acceptable forms from caller: `PROC`, `SCHEMA.PROC`, `DB.SCHEMA.PROC`, with or without `(...)`
	- Required form before calling `get_snowflake_ddl`: full procedure signature including parentheses and argument types, e.g. `DB.SCHEMA.PROC_NAME(NUMBER, VARCHAR)` or `DB.SCHEMA.PROC_NAME()`
- `object_type` — `PROCEDURE` (default), `TABLE`, `VIEW`, `FUNCTION`, `TASK`, `STREAM`

## Outputs
- `sql_text` — executable ETL code extracted from the DDL using the LLM extractor
- `source` — always `"snowflake_ddl_code"` when this skill runs
- `object_name` — resolved fully-qualified procedure signature used for GET_DDL, normalized to uppercase and preserving `(...)`
- `object_type` — echo of the resolved type

## Steps
1. Normalize and validate incoming `object_name`.
	- Trim whitespace, remove accidental trailing semicolon.
	- Reject names with leading/trailing dots or consecutive dots.
	- Parse optional signature suffix `(...)` if present.
2. Discover candidates with `list_stored_procedures`.
	- Match by procedure base name first (case-insensitive).
	- Prefer exact match when caller already provided a full signature.
3. Resolve to exactly one callable signature.
	- If one candidate exists, use it.
	- If multiple overloads exist and no exact signature was provided, return an ambiguity error that includes candidate signatures.
	- If no candidate exists, return `ObjectNotFound`.
4. Call `get_snowflake_ddl` using the resolved full signature (must include parentheses).
5. Call `extract_etl_code_from_ddl` on the returned DDL.
6. Return extracted `sql_text` and metadata, where `object_name` is the resolved signature actually used.

## Signature Rules (Critical)
- Never call `get_snowflake_ddl` with a bare procedure name.
- Always pass the resolved full signature, including `()` for no-arg procedures.
- Do not invent argument types. Use only signatures returned by `list_stored_procedures`.
- If signature resolution is ambiguous, fail fast with a clear error rather than guessing.

## Tools

### get_snowflake_ddl
Executes `SELECT GET_DDL('<object_type>', '<object_name>')` via a Snowpark session pinned to the `CODE_CRITIC_RO` role. Returns the raw DDL string.

**Parameters**

| name | type | required | description |
|------|------|----------|-------------|
| `object_name` | string | yes | Fully-qualified stored procedure signature (e.g. `DB.SCHEMA.PROC_NAME(NUMBER, VARCHAR)` or `DB.SCHEMA.PROC_NAME()`) |
| `object_type` | string | no | `PROCEDURE` (default), `TABLE`, `VIEW`, `FUNCTION`, `TASK`, `STREAM` |

**Returns**
```json
{ "ddl": "<DDL text>" }
```

**Errors**

| code | meaning |
|------|---------|
| `ObjectNotFound` | Object does not exist or `CODE_CRITIC_RO` lacks visibility |
| `InvalidIdentifier` | Name failed validation before the call was attempted |
| `ConnectionError` | Snowflake unreachable or Windows Credential Manager entry missing |

### extract_etl_code_from_ddl
Extracts executable ETL body from procedure DDL using an LLM prompt.

## LLM Extraction Prompt
Use this exact prompt as the system instruction for ETL extraction.

<!-- ETL_PROMPT_START -->
You extract executable ETL code from Snowflake DDL.
Return only code that should be reviewed by analyzers (procedure body or SQL logic), excluding DDL wrappers.
If the input is already executable SQL, return it unchanged.
Output must map cleanly to a structured field named etl_code.
<!-- ETL_PROMPT_END -->

**Parameters**

| name | type | required | description |
|------|------|----------|-------------|
| `ddl_text` | string | yes | Raw DDL returned by `get_snowflake_ddl` |

**Returns**
```json
{ "etl_code": "<executable ETL SQL/code>" }
```

## Edge Cases
- **Unknown object** — tool raises `ObjectNotFound`. Surface the error message verbatim; do not retry.
- **Invalid name format** — reject before calling the tool; return `{ "error": "InvalidIdentifier", "detail": "<reason>" }`.
- **Missing credential** — tool raises `ConnectionError`; forward the message asking the user to store the password in Windows Credential Manager.
- **Ambiguous 2-part name** — attempt lookup using the default database from `config.ini`; if that also fails, return `ObjectNotFound`.
- **Overloaded procedures without provided signature** — return `{ "error": "AmbiguousSignature", "detail": "Multiple overloads found", "candidates": ["..."] }`.
- **Input includes `PROC()` but Snowflake has only typed overloads** — do not guess; return `AmbiguousSignature` with candidate signatures.
