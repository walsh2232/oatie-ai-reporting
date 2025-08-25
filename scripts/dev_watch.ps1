<#!
.SYNOPSIS
  Development watchdog for Oatie platform.
.DESCRIPTION
  Monitors backend (FastAPI) and frontend (Vite) services. If either becomes unresponsive,
  the script terminates associated processes and restarts them with clean environment steps.
  Safe to re-run; uses process name & ports to detect existing instances.
.NOTES
  Requires PowerShell 5+ and Windows.
#>

param(
  [int]$BackendPort = 8000,
  [int]$FrontendPort = 5173,
  [int]$CheckIntervalSeconds = 15,
  [int]$UnhealthyThreshold = 3,
  [switch]$VerboseLog
)

$ErrorActionPreference = 'SilentlyContinue'

function Write-Log {
  param([string]$Message,[string]$Level = 'INFO')
  $ts = (Get-Date).ToString('s')
  Write-Host "[$ts][$Level] $Message"
}

function Test-PortHealthy {
  param([int]$Port,[string]$Path='/')
  try {
    $resp = Invoke-WebRequest -Uri "http://localhost:$Port$Path" -UseBasicParsing -TimeoutSec 5
    return $resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500
  } catch { return $false }
}

function Stop-IfRunning {
  param([string[]]$ProcessNames)
  foreach ($name in $ProcessNames) {
    Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
      Write-Log "Stopping process $($_.Id) ($name)" 'WARN'
      $_ | Stop-Process -Force
    }
  }
}

function Start-Backend {
  Write-Log 'Starting backend (virtual env + uvicorn)...'
  Push-Location "$PSScriptRoot/../backend"
  if (Test-Path .venv) { . .\.venv\Scripts\Activate.ps1 } else { Write-Log 'Virtual env missing - please create before running watchdog.' 'ERROR' }
  pip install -q -e . | Out-Null
  Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command','cd backend; . .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload' -WorkingDirectory (Get-Location).Path | Out-Null
  Pop-Location
}

function Start-Frontend {
  Write-Log 'Starting frontend (npm install + dev server)...'
  Push-Location "$PSScriptRoot/../frontend"
  if (-not (Test-Path node_modules)) { npm install --no-audit --no-fund | Out-Null }
  Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command','cd frontend; npm run dev' -WorkingDirectory (Get-Location).Path | Out-Null
  Pop-Location
}

# Tracking counters
$backendBad = 0
$frontendBad = 0

Write-Log "Watchdog starting. Backend:$BackendPort Frontend:$FrontendPort Interval:${CheckIntervalSeconds}s Threshold:$UnhealthyThreshold"

if (-not (Test-PortHealthy -Port $BackendPort -Path '/health/live')) { Start-Backend } else { Write-Log 'Backend already healthy.' }
if (-not (Test-PortHealthy -Port $FrontendPort)) { Start-Frontend } else { Write-Log 'Frontend already healthy.' }

while ($true) {
  Start-Sleep -Seconds $CheckIntervalSeconds

  $bHealthy = Test-PortHealthy -Port $BackendPort -Path '/health/live'
  $fHealthy = Test-PortHealthy -Port $FrontendPort

  if ($bHealthy) { $backendBad = 0; if ($VerboseLog) { Write-Log 'Backend healthy.' 'DEBUG' } } else { $backendBad++ }
  if ($fHealthy) { $frontendBad = 0; if ($VerboseLog) { Write-Log 'Frontend healthy.' 'DEBUG' } } else { $frontendBad++ }

  if ($backendBad -ge $UnhealthyThreshold) {
    Write-Log "Backend unhealthy for $backendBad consecutive checks. Restarting..." 'WARN'
    Stop-IfRunning -ProcessNames 'uvicorn','python'
    Start-Backend
    $backendBad = 0
  }

  if ($frontendBad -ge $UnhealthyThreshold) {
    Write-Log "Frontend unhealthy for $frontendBad consecutive checks. Restarting..." 'WARN'
    Stop-IfRunning -ProcessNames 'node','npm'
    Start-Frontend
    $frontendBad = 0
  }
}
