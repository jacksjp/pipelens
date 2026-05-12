#!/usr/bin/env bash
# Start the frontend dev server only (Vite on :5173).

set -euo pipefail
cd "$(dirname "$0")/../apps/frontend"

echo ">>> Starting frontend (:5173)"
npm run dev
