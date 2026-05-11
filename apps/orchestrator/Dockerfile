# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN pip install --no-cache-dir uv

WORKDIR /app

# Workspace metadata + lockfile (cache-friendly layer)
COPY pyproject.toml uv.lock ./
COPY packages/common/ packages/common/
COPY apps/orchestrator/ apps/orchestrator/

RUN uv sync --frozen --package orchestrator

EXPOSE 8000
ENV HOST=0.0.0.0 PORT=8000
CMD ["sh", "-c", "uv run --package orchestrator uvicorn orchestrator.main:app --host ${HOST} --port ${PORT}"]
