# Start required local services without Docker:
# mcp-server -> lint-auditor -> orchestrator -> frontend.

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$pidsFile = Join-Path $env:TEMP "pipelens.pids"
Set-Content -Path $pidsFile -Value ""

$jobs = @()

function Start-Bg {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [scriptblock]$ScriptBlock,
        [Parameter()]
        [string]$Name = ""
    )

    Write-Host ">>> Starting $Label"
    if ([string]::IsNullOrWhiteSpace($Name)) {
        $job = Start-Job -ScriptBlock $ScriptBlock
    } else {
        $job = Start-Job -Name $Name -ScriptBlock $ScriptBlock
    }

    $script:jobs += $job
    Add-Content -Path $pidsFile -Value $job.Id
}

function Stop-AllJobs {
    Write-Host "`n>>> Shutting down services"
    foreach ($j in $jobs) {
        try { Stop-Job -Job $j -ErrorAction SilentlyContinue } catch {}
        try { Remove-Job -Job $j -Force -ErrorAction SilentlyContinue } catch {}
    }
    if (Test-Path $pidsFile) {
        Remove-Item $pidsFile -Force -ErrorAction SilentlyContinue
    }
}

try {
    Write-Host ">>> Syncing workspace dependencies"
    uv sync

    Start-Bg -Label "mcp-server (:9000)" -Name "mcp-server" -ScriptBlock {
        Set-Location $using:PWD
        uv run --package mcp-server python -m mcp_server.server
    }

    Start-Sleep -Seconds 1

    Start-Bg -Label "lint-auditor (:8001)" -Name "agent-lint-auditor" -ScriptBlock {
        Set-Location $using:PWD
        $env:MCP_SERVER_URL = "http://127.0.0.1:9000/mcp"
        uv run --package agent-lint-auditor python -m agent_lint_auditor
    }

    Start-Sleep -Seconds 1

    Start-Bg -Label "orchestrator (:8000)" -Name "orchestrator" -ScriptBlock {
        Set-Location $using:PWD
        $env:AGENT_LINT_AUDITOR_URL = "http://127.0.0.1:8001"
        uv run --package orchestrator uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
    }

    Start-Sleep -Seconds 1

    Start-Bg -Label "frontend (:5173)" -Name "frontend" -ScriptBlock {
        Set-Location (Join-Path $using:PWD "apps/frontend")
        npm run dev
    }

    Write-Host ""
    Write-Host ">>> Services are up"
    Write-Host "MCP Server:   http://localhost:9000/mcp"
    Write-Host "Lint Auditor: http://localhost:8001"
    Write-Host "Orchestrator: http://localhost:8000"
    Write-Host "Frontend:     http://localhost:5173"
    Write-Host ">>> PIDs stored in $pidsFile"
    Write-Host ">>> Press Ctrl+C to stop all services"

    while ($true) {
        foreach ($j in $jobs) {
            Receive-Job -Job $j -Keep -ErrorAction SilentlyContinue | Out-Host
        }
        Start-Sleep -Seconds 2
    }
}
finally {
    Stop-AllJobs
}
