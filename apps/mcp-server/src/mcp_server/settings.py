"""Runtime settings for the MCP server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values read from environment / .env at startup."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 9000
    path: str = "/mcp"


settings = Settings()
