"""Factory for creating LangChain LLM instances with dynamic model selection."""

import os
from typing import Any, Literal, cast

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for an LLM model."""

    provider: Literal["openai", "anthropic", "google"]
    model_name: str = Field(
        description="Model identifier (e.g., gpt-4, claude-3-opus, gemini-2.0-flash)"
    )
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    api_key_env: str = Field(
        description="Environment variable name for API key (e.g., OPENAI_API_KEY)"
    )


class LLMFactory:
    """Factory for instantiating LangChain LLM models based on configuration."""

    @staticmethod
    def get_llm(model_config: ModelConfig) -> BaseChatModel:
        """
        Create and return a LangChain chat model instance.

        Args:
            model_config: ModelConfig with provider, model_name, and api_key_env

        Returns:
            Configured LangChain BaseChatModel instance (ChatOpenAI, ChatAnthropic, or ChatGoogleGenerativeAI)

        Raises:
            ValueError: If provider is unsupported or API key is missing
            ImportError: If required LangChain provider package is not installed
        """
        api_key = os.getenv(model_config.api_key_env)
        if not api_key:
            raise ValueError(
                f"API key for provider '{model_config.provider}' not found. "
                f"Set environment variable: {model_config.api_key_env}"
            )

        if model_config.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError as err:
                raise ImportError(
                    "langchain-openai is not installed. Run: pip install langchain-openai"
                ) from err

            openai_kwargs: dict[str, Any] = {
                "model": model_config.model_name,
                "temperature": model_config.temperature,
                "api_key": api_key,
            }
            if model_config.max_tokens is not None:
                openai_kwargs["max_tokens"] = model_config.max_tokens
            return cast(BaseChatModel, ChatOpenAI(**openai_kwargs))

        elif model_config.provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
            except ImportError as err:
                raise ImportError(
                    "langchain-anthropic is not installed. Run: pip install langchain-anthropic"
                ) from err

            anthropic_kwargs: dict[str, Any] = {
                "model": model_config.model_name,
                "temperature": model_config.temperature,
                "api_key": api_key,
            }
            if model_config.max_tokens is not None:
                anthropic_kwargs["max_tokens"] = model_config.max_tokens
            return cast(BaseChatModel, ChatAnthropic(**anthropic_kwargs))

        elif model_config.provider == "google":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError as err:
                raise ImportError(
                    "langchain-google-genai is not installed. Run: pip install langchain-google-genai"
                ) from err

            google_kwargs: dict[str, Any] = {
                "model": model_config.model_name,
                "temperature": model_config.temperature,
                "api_key": api_key,
            }
            if model_config.max_tokens is not None:
                google_kwargs["max_tokens"] = model_config.max_tokens
            return cast(BaseChatModel, ChatGoogleGenerativeAI(**google_kwargs))

        else:
            raise ValueError(
                f"Unsupported provider: {model_config.provider}. "
                f"Supported: openai, anthropic, google"
            )
