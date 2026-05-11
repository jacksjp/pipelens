#!/usr/bin/env bash
# Lint script for the project.
#   ./scripts/lint.sh           # check only (no changes)
#   ./scripts/lint.sh --fix     # auto-fix lint issues and reformat

set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--fix" ]]; then
    echo ">>> ruff check --fix"
    uv run ruff check --fix .
    echo ">>> ruff format"
    uv run ruff format .
    echo ">>> frontend prettier --write"
    (cd apps/frontend && npm run format) || true
    echo ">>> frontend eslint --fix"
    (cd apps/frontend && npx eslint . --fix --max-warnings=0) || true
else
    echo ">>> ruff check"
    uv run ruff check .
    echo ">>> ruff format --check"
    uv run ruff format --check .
    echo ">>> mypy"
    uv run mypy apps agents packages
    echo ">>> frontend prettier --check"
    (cd apps/frontend && npm run format:check)
    echo ">>> frontend eslint"
    (cd apps/frontend && npm run lint)
fi
