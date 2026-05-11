# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages/common/ packages/common/
COPY apps/mcp-server/ apps/mcp-server/

RUN uv sync --frozen --package mcp-server

EXPOSE 9000
ENV HOST=0.0.0.0 PORT=9000
CMD ["sh", "-c", "uv run --package mcp-server python -m mcp_server.server"]
