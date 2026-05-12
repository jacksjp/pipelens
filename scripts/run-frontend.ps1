# Start the frontend dev server only (Vite on :5173).

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host ">>> Starting frontend (:5173)"
Set-Location (Join-Path $PSScriptRoot "..\apps\frontend")
npm run dev
