# syntax=docker/dockerfile:1.7
# Generic Dockerfile shared by all agent services.
#
# Build context MUST be the repo root so the workspace lockfile and the
# `packages/common` package are visible. The agent is selected at build time
# via two args:
#   AGENT_NAME   = directory under agents/ (e.g. "lint-auditor")
#   AGENT_MODULE = importable Python module (e.g. "agent_lint_auditor")
#
# Example:
#   docker build -f agents/Dockerfile \
#     --build-arg AGENT_NAME=lint-auditor \
#     --build-arg AGENT_MODULE=agent_lint_auditor \
#     -t pipelens/agent-lint-auditor .

ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim AS base

ARG AGENT_NAME
ARG AGENT_MODULE
ENV AGENT_NAME=${AGENT_NAME} \
    AGENT_MODULE=${AGENT_MODULE} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN pip install --no-cache-dir uv

WORKDIR /app

# 1) Workspace metadata + lockfile (cache-friendly layer)
COPY pyproject.toml uv.lock ./
# 2) Shared package
COPY packages/common/ packages/common/
# 3) The selected agent's package only
COPY agents/${AGENT_NAME}/ agents/${AGENT_NAME}/

# 4) Install only this agent's package and its deps from the workspace
RUN uv sync --frozen --package agent-${AGENT_NAME}

EXPOSE 8000
ENV HOST=0.0.0.0 PORT=8000
CMD ["sh", "-c", "uv run python -m ${AGENT_MODULE}"]
