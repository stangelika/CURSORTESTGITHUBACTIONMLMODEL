param(
    [Parameter(Mandatory=$false)]
    [string]$Template = "docs\Report_Template.md",
    
    [Parameter(Mandatory=$false)]
    [string]$Output = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$OpenReport = $false
)

$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Message)
    Write-Host "📊 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)  
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Get-SafeOutput {
    param([scriptblock]$ScriptBlock, [string]$DefaultValue = "N/A")
    try {
        return & $ScriptBlock
    } catch {
        return $DefaultValue
    }
}

# Determine output file
if ([string]::IsNullOrEmpty($Output)) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $Output = "reports\cursor-agent-verify-$timestamp.md"
}

# Ensure output directory exists
$outputDir = Split-Path $Output -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

Write-Step "Generating automation report: $Output"

# Check if template exists
if (-not (Test-Path $Template)) {
    Write-Host "⚠️ Template not found: $Template. Using default template." -ForegroundColor Yellow
    $Template = $null
}

# Collect system information
Write-Step "Collecting system information..."

$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$repo = if (Test-Path ".git") { (git remote get-url origin) -replace "\.git$", "" -replace ".*github\.com[:/]", "" } else { "Unknown" }

# System info
$osInfo = Get-ComputerInfo | Select-Object -Property WindowsProductName, WindowsVersion
$gpuInfo = Get-SafeOutput { & "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe" --query-gpu=name --format=csv,noheader } "GPU info not available"
$pythonVersion = Get-SafeOutput { python --version } "Python not found"
$cursorVersion = Get-SafeOutput { 
    $cursorPath = Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\cursor" -Filter "Cursor.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cursorPath) { 
        (Get-ItemProperty $cursorPath.FullName).VersionInfo.FileVersion 
    } else { 
        "Not found" 
    }
} "Not found"

# Environment variables
$envVars = @{
    GITHUB_TOKEN = if ($env:GITHUB_TOKEN) { "present" } else { "absent" }
    CONTEXT7_API_KEY = if ($env:CONTEXT7_API_KEY) { "present" } else { "absent" }
}

# MCP status
Write-Step "Checking MCP servers..."
$mcpStatus = @{
    Context7 = "Unknown"
    Filesystem = "Unknown"  
    SQLite = "Unknown"
    Memory = "Unknown"
    GitHub = "Unknown"
}

if (Test-Path "scripts\check_mcp_setup.py") {
    try {
        $mcpOutput = python scripts\check_mcp_setup.py 2>&1
        # Parse output for MCP status (simplified)
        foreach ($line in $mcpOutput) {
            if ($line -match "Context7.*OK") { $mcpStatus.Context7 = "OK" }
            if ($line -match "Context7.*FAIL") { $mcpStatus.Context7 = "FAIL" }
            # Add similar parsing for other servers
        }
    } catch {
        Write-Host "⚠️ MCP check failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# GPU information
Write-Step "Collecting GPU information..."
$nvidiaSmiOutput = Get-SafeOutput { 
    & "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe" 2>$null
} "nvidia-smi not available"

# PyTorch info
$pytorchInfo = Get-SafeOutput {
    $output = python -c @"
import json, torch
info = {
    'version': torch.__version__,
    'cuda_available': torch.cuda.is_available(),
    'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
    'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
}
if torch.cuda.is_available():
    info['device_name'] = torch.cuda.get_device_name(0)
print(json.dumps(info, indent=2))
"@
    return $output
} "PyTorch not available"

# TensorFlow info  
$tensorflowInfo = Get-SafeOutput {
    $output = python -c @"
import json
try:
    import tensorflow as tf
    info = {
        'version': tf.__version__,
        'gpus': [gpu.name for gpu in tf.config.list_physical_devices('GPU')]
    }
except ImportError:
    info = {'error': 'TensorFlow not installed'}
print(json.dumps(info, indent=2))
"@
    return $output
} "TensorFlow not available"

# GitHub Actions info
Write-Step "Checking GitHub Actions..."
$actionsInfo = @{
    runner_status = "Unknown"
    latest_runs = @()
}

try {
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $runnerStatus = gh api repos/$repo/actions/runners --jq '.runners[] | select(.labels[].name == "gpu") | .status' 2>$null
        $actionsInfo.runner_status = if ($runnerStatus) { $runnerStatus } else { "offline" }
        
        $latestRuns = gh run list --limit 5 --json displayTitle,status,conclusion,url 2>$null | ConvertFrom-Json
        $actionsInfo.latest_runs = $latestRuns
    }
} catch {
    Write-Host "⚠️ GitHub CLI check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Build report content
Write-Step "Building report content..."

if ($Template -and (Test-Path $Template)) {
    $reportContent = Get-Content $Template -Raw
    
    # Replace placeholders
    $reportContent = $reportContent -replace '\{\{date\}\}', $date
    $reportContent = $reportContent -replace '\{\{repo\}\}', $repo
    $reportContent = $reportContent -replace '\{\{cursor_version\}\}', $cursorVersion
    $reportContent = $reportContent -replace '\{\{present\|absent\}\}', $envVars.CONTEXT7_API_KEY
    $reportContent = $reportContent -replace '\{\{nvidia_smi\}\}', $nvidiaSmiOutput
    $reportContent = $reportContent -replace '\{\{torch_info_json\}\}', $pytorchInfo
    $reportContent = $reportContent -replace '\{\{tf_info_json\}\}', $tensorflowInfo
    $reportContent = $reportContent -replace '\{\{online\|offline\}\}', $actionsInfo.runner_status
    
} else {
    # Default report template
    $reportContent = @"
# ML Workstation Automation Report

Generated: $date
Repository: $repo

## System Information
- OS: $($osInfo.WindowsProductName) $($osInfo.WindowsVersion)
- GPU: $gpuInfo
- Python: $pythonVersion
- Cursor: $cursorVersion

## Environment Variables
- GITHUB_TOKEN: $($envVars.GITHUB_TOKEN)
- CONTEXT7_API_KEY: $($envVars.CONTEXT7_API_KEY)

## MCP Server Status
- Context7: $($mcpStatus.Context7)
- Filesystem: $($mcpStatus.Filesystem)
- SQLite: $($mcpStatus.SQLite)
- Memory: $($mcpStatus.Memory)
- GitHub: $($mcpStatus.GitHub)

## GPU Information
``````
$nvidiaSmiOutput
``````

## PyTorch Information
``````json
$pytorchInfo
``````

## TensorFlow Information
``````json
$tensorflowInfo
``````

## GitHub Actions
- Runner Status: $($actionsInfo.runner_status)
- Latest Runs: $($actionsInfo.latest_runs.Count) available

## Generated by
Script: generate_report.ps1
Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
}

# Save report
$reportContent | Out-File -FilePath $Output -Encoding UTF8
Write-Success "Report generated: $Output"

# Open report if requested
if ($OpenReport) {
    try {
        Start-Process $Output
        Write-Success "Report opened"
    } catch {
        Write-Host "⚠️ Could not open report: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Step "Report generation completed!"