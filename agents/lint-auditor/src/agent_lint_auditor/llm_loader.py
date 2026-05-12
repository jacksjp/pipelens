"""Load and instantiate LLM models for the lint-auditor agent."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

import yaml
from common import LLMFactory, ModelConfig
from langchain_core.language_models import BaseChatModel


def load_agents_config(config_path: str | None = None) -> dict[str, Any]:
    """
    Load agents.yaml configuration file.

    Args:
        config_path: Path to agents.yaml. If None, searches in project root and cwd.

    Returns:
        Parsed YAML as dictionary

    Raises:
        FileNotFoundError: If agents.yaml not found
        yaml.YAMLError: If YAML parsing fails
    """
    if config_path is None:
        # Search in common locations
        search_paths = [
            Path("./agents.yaml"),
            Path("../agents.yaml"),
            Path("../../agents.yaml"),
            Path(os.getenv("AGENTS_CONFIG_PATH", "")),
        ]
        config_path = None
        for path in search_paths:
            if path.exists():
                config_path = str(path)
                break

        if config_path is None:
            raise FileNotFoundError(
                "agents.yaml not found. Search paths: "
                f"{[str(p) for p in search_paths if p != Path(os.getenv('AGENTS_CONFIG_PATH', ''))]}. "
                "Set AGENTS_CONFIG_PATH environment variable to specify custom location."
            )

    with open(config_path) as f:
        loaded = yaml.safe_load(f)
    if not isinstance(loaded, dict):
        raise ValueError("agents.yaml must contain a top-level mapping")
    return cast(dict[str, Any], loaded)


def get_llm_for_agent(
    model_name: str, agents_config: dict[str, Any] | None = None
) -> BaseChatModel:
    """
    Get a configured LLM for the specified model name.

    Args:
        model_name: Key of the model in agents.yaml (e.g., "claude-sonnet", "gpt-4")
        agents_config: Pre-loaded agents config dict. If None, loads from agents.yaml.

    Returns:
        Configured LangChain BaseChatModel instance

    Raises:
        ValueError: If model not found in config
        ValueError: If provider/api_key not configured properly
    """
    if agents_config is None:
        agents_config = load_agents_config()

    models_config = agents_config.get("models", {})
    if not isinstance(models_config, dict):
        raise ValueError("Invalid agents.yaml: 'models' must be a mapping")
    if model_name not in models_config:
        available = list(models_config.keys())
        raise ValueError(
            f"Model '{model_name}' not found in agents.yaml. Available models: {available}"
        )

    model_def = models_config[model_name]
    if not isinstance(model_def, dict):
        raise ValueError(f"Invalid model config for '{model_name}'")
    model_config = ModelConfig(**model_def)

    return LLMFactory.get_llm(model_config)


def get_default_model_for_agent(
    agent_name: str, agents_config: dict[str, Any] | None = None
) -> str:
    """
    Get the default model name for an agent.

    Args:
        agent_name: Agent name (e.g., "lint-auditor")
        agents_config: Pre-loaded agents config dict. If None, loads from agents.yaml.

    Returns:
        Default model name

    Raises:
        ValueError: If agent not found or no default model specified
    """
    if agents_config is None:
        agents_config = load_agents_config()

    agents = agents_config.get("agents", {})
    if not isinstance(agents, dict):
        raise ValueError("Invalid agents.yaml: 'agents' must be a mapping")
    if agent_name not in agents:
        raise ValueError(
            f"Agent '{agent_name}' not found in agents.yaml. "
            f"Available agents: {list(agents.keys())}"
        )

    agent_config = agents[agent_name]
    if not isinstance(agent_config, dict):
        raise ValueError(f"Invalid config for agent '{agent_name}'")
    default_model = agent_config.get("default_model")
    if not isinstance(default_model, str) or not default_model:
        raise ValueError(f"No default_model specified for agent '{agent_name}' in agents.yaml")

    return default_model


def get_agent_config(
    agent_name: str, agents_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Get agent configuration (max_retries, description, etc.).

    Args:
        agent_name: Agent name (e.g., "lint-auditor")
        agents_config: Pre-loaded agents config dict. If None, loads from agents.yaml.

    Returns:
        Agent configuration dictionary

    Raises:
        ValueError: If agent not found
    """
    if agents_config is None:
        agents_config = load_agents_config()

    agents = agents_config.get("agents", {})
    if not isinstance(agents, dict):
        raise ValueError("Invalid agents.yaml: 'agents' must be a mapping")
    if agent_name not in agents:
        raise ValueError(
            f"Agent '{agent_name}' not found in agents.yaml. "
            f"Available agents: {list(agents.keys())}"
        )

    agent_config = agents[agent_name]
    if not isinstance(agent_config, dict):
        raise ValueError(f"Invalid config for agent '{agent_name}'")
    return cast(dict[str, Any], agent_config)
