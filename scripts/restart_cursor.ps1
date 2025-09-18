param(
    [Parameter(Mandatory=$false)]
    [string]$CursorPath = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$KillOnly = $false
)

$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Message)
    Write-Host "🔄 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

Write-Step "Restarting Cursor for MCP configuration reload..."

# Find Cursor installation if path not provided
if ([string]::IsNullOrEmpty($CursorPath)) {
    $possiblePaths = @(
        "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe",
        "$env:PROGRAMFILES\Cursor\Cursor.exe", 
        "$env:USERPROFILE\AppData\Local\Programs\cursor\Cursor.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $CursorPath = $path
            break
        }
    }
    
    if ([string]::IsNullOrEmpty($CursorPath)) {
        Write-Warning "Cursor installation not found. Please provide path with -CursorPath parameter."
        Write-Step "Common locations to check:"
        foreach ($path in $possiblePaths) {
            Write-Host "  - $path" -ForegroundColor Gray
        }
        exit 1
    }
}

Write-Step "Using Cursor path: $CursorPath"

# Kill existing Cursor processes
Write-Step "Stopping existing Cursor processes..."
$cursorProcesses = Get-Process -Name "Cursor*" -ErrorAction SilentlyContinue

if ($cursorProcesses) {
    foreach ($process in $cursorProcesses) {
        try {
            Write-Host "Stopping process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Gray
            Stop-Process -Id $process.Id -Force
        } catch {
            Write-Warning "Failed to stop process $($process.Id): $($_.Exception.Message)"
        }
    }
    
    # Wait for processes to fully exit
    Write-Step "Waiting for processes to exit..."
    Start-Sleep -Seconds 3
    
    # Check if any processes are still running
    $remainingProcesses = Get-Process -Name "Cursor*" -ErrorAction SilentlyContinue
    if ($remainingProcesses) {
        Write-Warning "Some Cursor processes are still running:"
        foreach ($process in $remainingProcesses) {
            Write-Host "  - $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
        }
    } else {
        Write-Success "All Cursor processes stopped successfully"
    }
} else {
    Write-Step "No Cursor processes found running"
}

if ($KillOnly) {
    Write-Success "Cursor processes killed. Exiting (KillOnly mode)."
    exit 0
}

# Clear MCP cache/logs to force reload
Write-Step "Clearing MCP caches..."
$mcpCachePaths = @(
    "$env:APPDATA\Cursor\logs",
    "$env:APPDATA\Cursor\CachedExtensions",
    "$env:TEMP\cursor*"
)

foreach ($cachePath in $mcpCachePaths) {
    if (Test-Path $cachePath) {
        try {
            Get-ChildItem -Path $cachePath -Recurse -File | 
                Where-Object { $_.Name -match "(mcp|log)" } | 
                Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "Cleared cache: $cachePath" -ForegroundColor Gray
        } catch {
            Write-Warning "Could not clear cache: $cachePath"
        }
    }
}

# Restart Cursor
Write-Step "Starting Cursor..."
try {
    $currentDir = Get-Location
    Start-Process -FilePath $CursorPath -WorkingDirectory $currentDir.Path
    
    Write-Success "Cursor started successfully"
    
    Write-Step "Next steps:"
    Write-Host "1. Wait 1-2 minutes for Cursor to fully load" -ForegroundColor White
    Write-Host "2. Wait for MCP servers to initialize (check status bar)" -ForegroundColor White
    Write-Host "3. Open a new chat to test MCP functionality" -ForegroundColor White
    Write-Host "4. If MCP servers don't load, check:" -ForegroundColor White
    Write-Host "   - Docker is running (for GitHub MCP)" -ForegroundColor White
    Write-Host "   - Environment variables are set" -ForegroundColor White
    Write-Host "   - MCP configuration file exists" -ForegroundColor White
    
    # Optional: Run MCP validation after a delay
    Write-Step "Scheduling MCP validation check in 30 seconds..."
    Start-Sleep -Seconds 30
    
    if (Test-Path "scripts\check_mcp_setup.py") {
        Write-Step "Running MCP validation..."
        python scripts\check_mcp_setup.py
    }
    
} catch {
    Write-Warning "Failed to start Cursor: $($_.Exception.Message)"
    Write-Step "Try starting Cursor manually from: $CursorPath"
    exit 1
}

Write-Success "Cursor restart completed!"