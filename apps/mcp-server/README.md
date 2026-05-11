# mcp-server

FastMCP server exposing shared tools (Snowflake DDL fetch, ETL extraction)
to the Code Critic agents over the streamable-http transport.

## Exposed tools

- `ping()`
- `lint_fix_sql(sql_text, user_dialect=None)`
- `lint_fix_python(python_text)`

Both lint-fix tools return the same state payload shape:

- `initial_errors`
- `fixed_errors`
- `final_chunk`
- `final_errors`

## Run locally

```bash
uv run --package mcp-server python -m mcp_server.server
```

Snowflake-backed tools require the optional `snowflake` extra:

```bash
uv sync --package mcp-server --extra snowflake
```
