"""Runtime settings for the orchestrator, sourced from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values read from environment / .env at startup."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000

    agent_lint_auditor_url: str = "http://127.0.0.1:8001"
    mcp_server_url: str = "http://127.0.0.1:9000/mcp"
    agents_config_path: str = "./agents.yaml"


settings = Settings()
