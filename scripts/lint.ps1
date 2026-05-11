# Lint script — Windows / PowerShell mirror of scripts/lint.sh.
# Usage: scripts/lint.ps1            # check only
#        scripts/lint.ps1 -Fix       # auto-fix lint issues and reformat

param([switch]$Fix)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if ($Fix) {
    Write-Host ">>> ruff check --fix"
    uv run ruff check --fix .
    Write-Host ">>> ruff format"
    uv run ruff format .
    Write-Host ">>> frontend prettier --write"
    Push-Location apps/frontend; try { npm run format } finally { Pop-Location }
    Write-Host ">>> frontend eslint --fix"
    Push-Location apps/frontend; try { npx eslint . --fix --max-warnings=0 } finally { Pop-Location }
} else {
    Write-Host ">>> ruff check"
    uv run ruff check .
    Write-Host ">>> ruff format --check"
    uv run ruff format --check .
    Write-Host ">>> mypy"
    uv run mypy apps agents packages
    Write-Host ">>> frontend prettier --check"
    Push-Location apps/frontend; try { npm run format:check } finally { Pop-Location }
    Write-Host ">>> frontend eslint"
    Push-Location apps/frontend; try { npm run lint } finally { Pop-Location }
}
