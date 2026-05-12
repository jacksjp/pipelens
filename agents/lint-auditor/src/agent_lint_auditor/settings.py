"""Runtime settings for the lint-auditor agent."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values read from environment / .env at startup."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8001
    mcp_server_url: str = "http://127.0.0.1:9000/mcp"

    # Path to agents.yaml (for model configuration)
    agents_config_path: str = "./agents.yaml"

    # Agent name (used to look up default model in agents.yaml)
    agent_name: str = "lint-auditor"


settings = Settings()
