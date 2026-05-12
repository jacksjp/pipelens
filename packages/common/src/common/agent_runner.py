"""Minimal HTTP wrapper used by every agent service.

Exposes `/health`, `/card`, and `/execute` — mirroring the A2A SDK surface
so switching to `a2a-sdk` later is a one-file change inside each agent.
"""

from collections.abc import Callable
from typing import Any, cast

from fastapi import FastAPI
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from common.schemas import AgentInput, AgentOutput

ExecutorFn = Callable[[AgentInput], AgentOutput]


def _card_to_dict(card: Any) -> dict[str, Any]:
    """Convert an AgentCard protobuf or plain dict to a JSON-serializable dict."""
    if isinstance(card, Message):
        return cast(dict[str, Any], MessageToDict(card))

    if isinstance(card, dict):
        return cast(dict[str, Any], card)

    if hasattr(card, "model_dump"):
        dumped = card.model_dump()
        if isinstance(dumped, dict):
            return cast(dict[str, Any], dumped)

    raise TypeError("card must be a protobuf Message, dict, or pydantic-like object")


def create_agent_app(card: Any, executor: ExecutorFn) -> FastAPI:
    """Build a FastAPI app exposing the standard agent endpoints."""
    card_dict = _card_to_dict(card)
    app = FastAPI(title=card_dict.get("name", "agent"), version=card_dict.get("version", "0.1.0"))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/card")
    def get_card() -> dict[str, Any]:
        return card_dict

    @app.post("/execute")
    def execute(payload: AgentInput) -> AgentOutput:
        return executor(payload)

    return app


def run_agent(
    card: Any,
    executor: ExecutorFn,
    *,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    """Run the agent's HTTP server with uvicorn."""
    import uvicorn

    app = create_agent_app(card, executor)
    uvicorn.run(app, host=host, port=port)
