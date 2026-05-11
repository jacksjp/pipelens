#!/usr/bin/env bash
# Start required local services without Docker:
# mcp-server -> lint-auditor -> orchestrator -> frontend.

set -euo pipefail
cd "$(dirname "$0")/.."

PIDS_FILE="/tmp/pipelens.pids"
: > "$PIDS_FILE"

PIDS=()
cleanup() {
    echo
    echo ">>> Shutting down services"
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

start_bg "lint-auditor (:8001)" env MCP_SERVER_URL=http://127.0.0.1:9000/mcp uv run --package agent-lint-auditor python -m agent_lint_auditor
sleep 1

start_bg "orchestrator (:8000)" env AGENT_LINT_AUDITOR_URL=http://127.0.0.1:8001 uv run --package orchestrator uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
sleep 1

start_bg "frontend (:5173)" bash -lc "cd apps/frontend && npm run dev"

echo

echo ">>> Services are up"
echo "MCP Server:   http://localhost:9000/mcp"
echo "Lint Auditor: http://localhost:8001"
echo "Orchestrator: http://localhost:8000"
echo "Frontend:     http://localhost:5173"
echo ">>> PIDs stored in ${PIDS_FILE}"
echo ">>> Press Ctrl+C to stop all services"

wait
