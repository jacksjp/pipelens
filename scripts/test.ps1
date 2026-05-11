# Run all tests across the workspace.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host ">>> Python: pytest"
uv run pytest

Write-Host ">>> Frontend: vitest"
Push-Location apps/frontend
try { npm test } finally { Pop-Location }
