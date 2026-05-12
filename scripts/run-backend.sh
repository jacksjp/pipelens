#!/usr/bin/env bash
# Start backend services only (mcp-server, lint-auditor, orchestrator).

set -euo pipefail
cd "$(dirname "$0")/.."

DEBUG=0
if [[ "${1:-}" == "--debug" ]]; then
    DEBUG=1
    shift
fi

if [[ "$DEBUG" -eq 1 ]]; then
    echo ">>> Debug mode enabled (reload where supported)"
    echo ">>> Note: mcp-server still runs without reload"
fi

PIDS_FILE="/tmp/pipelens-backend.pids"
: > "$PIDS_FILE"

PIDS=()
cleanup() {
    echo
    echo ">>> Shutting down backend services"
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    rm -f "$PIDS_FILE"
}
trap cleanup INT TERM EXIT

start_bg() {
    local label="$1"
    shift
    echo ">>> Starting ${label}"
    "$@" &
    local pid=$!
    PIDS+=("$pid")
    echo "$pid" >> "$PIDS_FILE"
}

echo ">>> Syncing workspace dependencies"
uv sync

start_bg "mcp-server (:9000)" uv run --package mcp-server python -m mcp_server.server
sleep 1

if [[ "$DEBUG" -eq 1 ]]; then
    start_bg "lint-auditor (:8001)" env MCP_SERVER_URL=http://127.0.0.1:9000/mcp uv run --package agent-lint-auditor uvicorn agent_lint_auditor.__main__:app --host 0.0.0.0 --port 8001 --reload
else
    start_bg "lint-auditor (:8001)" env MCP_SERVER_URL=http://127.0.0.1:9000/mcp uv run --package agent-lint-auditor python -m agent_lint_auditor
fi
sleep 1

if [[ "$DEBUG" -eq 1 ]]; then
    start_bg "orchestrator (:8000)" env AGENT_LINT_AUDITOR_URL=http://127.0.0.1:8001 uv run --package orchestrator uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
else
    start_bg "orchestrator (:8000)" env AGENT_LINT_AUDITOR_URL=http://127.0.0.1:8001 uv run --package orchestrator uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000
fi

echo
echo ">>> Backend services are up"
echo "MCP Server:   http://localhost:9000/mcp"
echo "Lint Auditor: http://localhost:8001"
echo "Orchestrator: http://localhost:8000"
echo ">>> PIDs stored in ${PIDS_FILE}"
echo ">>> Press Ctrl+C to stop all services"

wait
