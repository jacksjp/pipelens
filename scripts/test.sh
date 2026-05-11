#!/usr/bin/env bash
# Run all tests across the workspace.

set -euo pipefail
cd "$(dirname "$0")/.."

echo ">>> Python: pytest"
uv run pytest

echo ">>> Frontend: vitest"
(cd apps/frontend && npm test)
