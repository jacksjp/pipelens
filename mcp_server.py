"""FastMCP server exposing Code Critic tools and prompts."""

import keyring
from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from snowflake.snowpark import Session

from prompts import (
    PERFORMANCE_ANALYZER_SKILL,
    ROUTER_SKILL,
    SCHEMA_FETCHER_ETL_PROMPT,
    SCHEMA_FETCHER_SKILL,
    SECURITY_AUDITOR_SKILL,
    STYLE_REVIEWER_SKILL,
    SYNTHESIZER_SKILL,
)

load_dotenv()

# ── LLM singletons ────────────────────────────────────────────────────────────
GEMMA_MODEL = "gemma-4-26b-a4b-it"
OPUS_MODEL = "claude-opus-4-6"
SONNET_MODEL = "claude-sonnet-4-6"

ALLOWED_OBJECT_TYPES = {"PROCEDURE", "TABLE", "VIEW", "FUNCTION", "TASK", "STREAM"}

gemma_llm = ChatGoogleGenerativeAI(model=GEMMA_MODEL)
opus_llm = ChatAnthropic(model=OPUS_MODEL)
sonnet_llm = ChatAnthropic(model=SONNET_MODEL)


# ── Snowflake helper ──────────────────────────────────────────────────────────
def _get_snowpark_session() -> Session:
    return Session.builder.configs(
        {
            "account": "XBIGDOM-TJ90709",
            "user": "DDL_READER_CODE_CRITIC",
            "password": keyring.get_password("snowflake", "DDL_READER_CODE_CRITIC"),
            "role": "ROLE_DDL_READONLY_CODE_CRITIC",
            "database": "bronze",
            "schema": "public",
        }
    ).create()


# ── Pydantic model ────────────────────────────────────────────────────────────
class ETLExtractionResult(BaseModel):
    """Structured output for LLM-based ETL code extraction."""

    etl_code: str


def _is_not_found_error(error_text: str) -> bool:
    """Best-effort detection for Snowflake object-not-found errors."""
    text = (error_text or "").lower()
    markers = [
        "does not exist",
        "not exist",
        "unknown",
        "not found",
        "object does not exist",
    ]
    return any(marker in text for marker in markers)


# ── FastMCP server ────────────────────────────────────────────────────────────
mcp = FastMCP("code-critic")


# ── Tools ─────────────────────────────────────────────────────────────────────
@mcp.tool()
def get_snowflake_ddl(object_name: str, object_type: str = "PROCEDURE") -> str:
    """Fetch the raw DDL text for a named Snowflake object.

    Executes SELECT GET_DDL('<object_type>', '<object_name>') via a Snowpark
    session using the DDL_READER_CODE_CRITIC service account.
    """
    normalized_type = object_type.upper()
    if normalized_type not in ALLOWED_OBJECT_TYPES:
        raise ValueError(
            f"Unsupported object_type '{object_type}'. " f"Allowed: {sorted(ALLOWED_OBJECT_TYPES)}"
        )
    safe_name = object_name.replace("'", "''")
    session = _get_snowpark_session()
    try:
        result = session.sql(f"SELECT GET_DDL('{normalized_type}', '{safe_name}')").collect()
        return result[0][0]
    finally:
        session.close()


@mcp.tool()
def list_snowflake_stored_procedures(database: str = "bronze", schema: str = "public") -> list[str]:
    """List all stored procedures in a Snowflake database and schema.

    Returns a list of fully-qualified procedure signatures in the form
    DATABASE.SCHEMA.PROCEDURE_NAME(ARG_TYPES).
    """
    safe_db = database.replace("'", "''")
    safe_schema = schema.replace("'", "''")
    session = _get_snowpark_session()
    try:
        rows = session.sql(
            f"SHOW PROCEDURES IN SCHEMA {safe_db}.{safe_schema}"
        ).collect()
        return [row["name"] for row in rows]
    finally:
        session.close()


@mcp.tool()
def extract_etl_code_from_ddl(ddl_text: str) -> str:
    """Extract executable ETL body from Snowflake procedure DDL using an LLM.

    Uses the ETL extraction prompt from skills/schema-fetcher/SKILL.md.
    Falls back to the raw DDL if structured extraction fails.
    """
    if not ddl_text:
        return ""
    extraction_chain = gemma_llm.with_structured_output(ETLExtractionResult)
    human_prompt = f"Extract ETL code from this Snowflake DDL:\n\n{ddl_text}"
    try:
        result = extraction_chain.invoke(
            [
                SystemMessage(content=SCHEMA_FETCHER_ETL_PROMPT),
                HumanMessage(content=human_prompt),
            ]
        )
        return (result.etl_code or "").strip()
    except Exception:
        return ddl_text.strip()


@mcp.tool()
def schema_fetcher_tool(object_name: str) -> dict:
    """Fetch stored procedure DDL and return extracted ETL in one call.

    Returns a structured payload with status and message:
    - status=done: DDL fetched and ETL extracted
    - status=error: proc not found or fetch failed
    """
    try:
        ddl = get_snowflake_ddl(object_name=object_name, object_type="PROCEDURE")
    except Exception as exc:
        error_text = str(exc)
        message = "Stored proc not found." if _is_not_found_error(error_text) else "Unable to fetch stored proc."
        return {
            "status": "error",
            "message": message,
            "object_name": object_name,
            "object_type": "PROCEDURE",
            "etl_code": None,
            "raw_ddl": None,
            "raw_ddl_length": 0,
            "fetch_error": error_text,
        }

    etl_code = extract_etl_code_from_ddl(ddl)
    return {
        "status": "done",
        "message": f"ETL script extracted successfully ({len(etl_code)} chars).",
        "object_name": object_name,
        "object_type": "PROCEDURE",
        "etl_code": etl_code,
        "raw_ddl": ddl,
        "raw_ddl_length": len(ddl),
        "fetch_error": None,
    }


# ── Prompts ───────────────────────────────────────────────────────────────────
@mcp.prompt()
def router_skill() -> str:
    """Classify raw user input as sql_query, stored_procedure, or unknown."""
    return ROUTER_SKILL


@mcp.prompt()
def schema_fetcher_skill() -> str:
    """Full schema-fetcher role: steps, tools, and edge cases."""
    return SCHEMA_FETCHER_SKILL


@mcp.prompt()
def schema_fetcher_etl_prompt() -> str:
    """System prompt for LLM-based ETL code extraction from Snowflake DDL."""
    return SCHEMA_FETCHER_ETL_PROMPT


@mcp.prompt()
def performance_analyzer_skill() -> str:
    """Detect performance inefficiencies in SQL queries and stored procedures."""
    return PERFORMANCE_ANALYZER_SKILL


@mcp.prompt()
def security_auditor_skill() -> str:
    """Flag security vulnerabilities in SQL queries and stored procedures."""
    return SECURITY_AUDITOR_SKILL


@mcp.prompt()
def style_reviewer_skill() -> str:
    """Catch style and readability violations in SQL queries and stored procedures."""
    return STYLE_REVIEWER_SKILL


@mcp.prompt()
def synthesizer_skill() -> str:
    """Merge and rank findings from all analyzer nodes into a final report."""
    return SYNTHESIZER_SKILL


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=9000, path="/mcp")
