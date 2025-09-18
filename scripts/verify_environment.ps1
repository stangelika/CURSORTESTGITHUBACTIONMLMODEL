param(
    [Parameter(Mandatory=$false)]
    [switch]$Quick = $false
)

$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Message)
    Write-Host "🔍 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Test-Command {
    param([string]$Command, [string]$Description)
    
    try {
        $output = Invoke-Expression "$Command --version" 2>&1
        Write-Success "$Description`: $($output | Select-Object -First 1)"
        return $true
    } catch {
        Write-Error "$Description not found or not working"
        return $false
    }
}

function Test-PythonPackage {
    param([string]$Package, [string]$ImportName = $Package)
    
    try {
        $version = python -c "import $ImportName; print($ImportName.__version__)" 2>$null
        if ($version) {
            Write-Success "$Package`: $version"
            return $true
        } else {
            Write-Error "$Package`: Not available or no version info"
            return $false
        }
    } catch {
        Write-Error "$Package`: Not installed"
        return $false
    }
}

Write-Step "ML Workstation Environment Verification"
Write-Host "=" * 50

# System Information
Write-Step "System Information"
$osInfo = Get-ComputerInfo | Select-Object -Property WindowsProductName, WindowsVersion, WindowsDisplayVersion
Write-Host "OS: $($osInfo.WindowsProductName) $($osInfo.WindowsVersion) ($($osInfo.WindowsDisplayVersion))" -ForegroundColor White

# Core Tools
Write-Step "Core Development Tools"
$toolsOk = 0
$toolsOk += if (Test-Command "python" "Python") { 1 } else { 0 }
$toolsOk += if (Test-Command "git" "Git") { 1 } else { 0 }
$toolsOk += if (Test-Command "docker" "Docker") { 1 } else { 0 }

# Optional tools
if (Test-Command "gh" "GitHub CLI") { $toolsOk++ }
if (Test-Command "node" "Node.js") { $toolsOk++ }
if (Test-Command "npm" "NPM") { $toolsOk++ }

# Environment Variables
Write-Step "Environment Variables"
$envOk = 0

$githubToken = $env:GITHUB_TOKEN
if ($githubToken) {
    Write-Success "GITHUB_TOKEN: Set (length: $($githubToken.Length))"
    $envOk++
} else {
    Write-Error "GITHUB_TOKEN: Not set"
}

$context7Key = $env:CONTEXT7_API_KEY  
if ($context7Key) {
    Write-Success "CONTEXT7_API_KEY: Set (length: $($context7Key.Length))"
    $envOk++
} else {
    Write-Warning "CONTEXT7_API_KEY: Not set (optional)"
}

# Python Environment
Write-Step "Python Environment"
$pythonOk = 0

try {
    $pythonInfo = python -c @"
import sys, platform
print(f'Version: {sys.version}')
print(f'Executable: {sys.executable}')  
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()[0]}')
"@
    
    Write-Host $pythonInfo -ForegroundColor White
    $pythonOk++
} catch {
    Write-Error "Failed to get Python info"
}

# ML Packages
Write-Step "Machine Learning Packages"
$mlOk = 0
$mlOk += if (Test-PythonPackage "torch") { 1 } else { 0 }
$mlOk += if (Test-PythonPackage "numpy") { 1 } else { 0 }  
$mlOk += if (Test-PythonPackage "pandas") { 1 } else { 0 }
$mlOk += if (Test-PythonPackage "sklearn" "sklearn") { 1 } else { 0 }

# Optional ML packages
if (Test-PythonPackage "tensorflow" "tensorflow") { $mlOk++ }
if (Test-PythonPackage "matplotlib") { $mlOk++ }
if (Test-PythonPackage "pynvml") { $mlOk++ }

# GPU/CUDA Check
Write-Step "GPU and CUDA"
$gpuOk = 0

# NVIDIA SMI
try {
    $nvidiaSmi = & "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe" --query-gpu=name,driver_version --format=csv,noheader 2>$null
    if ($nvidiaSmi) {
        Write-Success "NVIDIA Driver: $nvidiaSmi"
        $gpuOk++
    } else {
        Write-Error "NVIDIA SMI: Not working"
    }
} catch {
    Write-Error "NVIDIA SMI: Not found"
}

# PyTorch CUDA
try {
    $torchCuda = python -c @"
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'Device Count: {torch.cuda.device_count()}')
    print(f'Device 0: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory // 1024 // 1024} MB')
"@ 2>$null
    
    if ($torchCuda -match "CUDA Available: True") {
        Write-Success "PyTorch CUDA: Available"
        Write-Host $torchCuda -ForegroundColor White
        $gpuOk++
    } else {
        Write-Warning "PyTorch CUDA: Not available (CPU only)"
        Write-Host $torchCuda -ForegroundColor Yellow
    }
} catch {
    Write-Error "PyTorch CUDA: Cannot check"
}

if (-not $Quick) {
    # MCP Configuration
    Write-Step "MCP Configuration"
    $mcpOk = 0
    
    if (Test-Path "scripts\check_mcp_setup.py") {
        try {
            python scripts\check_mcp_setup.py
            $mcpOk++
        } catch {
            Write-Warning "MCP check script failed"
        }
    } else {
        Write-Warning "MCP check script not found"
    }
    
    # GitHub Actions
    Write-Step "GitHub Actions"
    $actionsOk = 0
    
    if (Test-Path ".github\workflows") {
        $workflows = Get-ChildItem -Path ".github\workflows" -Filter "*.yml"
        Write-Success "Workflows found: $($workflows.Count)"
        foreach ($workflow in $workflows) {
            Write-Host "  - $($workflow.BaseName)" -ForegroundColor Gray
        }
        $actionsOk++
    } else {
        Write-Warning "No workflows directory found"
    }
    
    # Runner status (if GitHub CLI available)
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        try {
            $repo = git remote get-url origin 2>$null | ForEach-Object { $_ -replace "\.git$", "" -replace ".*github\.com[:/]", "" }
            if ($repo) {
                $runners = gh api "repos/$repo/actions/runners" --jq '.runners[] | select(.labels[].name == "gpu") | .status' 2>$null
                if ($runners) {
                    Write-Success "Self-hosted GPU runner: $runners"
                    $actionsOk++
                } else {
                    Write-Warning "No GPU runners found"
                }
            }
        } catch {
            Write-Warning "Could not check runner status"
        }
    }
    
    # Project Structure
    Write-Step "Project Structure"
    $structureOk = 0
    
    $requiredDirs = @("scripts", "experiments", "docs")
    foreach ($dir in $requiredDirs) {
        if (Test-Path $dir) {
            Write-Success "Directory $dir`: exists"
            $structureOk++
        } else {
            Write-Warning "Directory $dir`: missing"
        }
    }
    
    $importantFiles = @(
        "requirements.txt",
        "experiments\train.py", 
        "scripts\gpu_monitor.py",
        "docs\Automation_Runbook.md"
    )
    
    foreach ($file in $importantFiles) {
        if (Test-Path $file) {
            Write-Success "File $file`: exists"
            $structureOk++
        } else {
            Write-Warning "File $file`: missing"
        }
    }
}

# Summary
Write-Step "Verification Summary"
Write-Host "=" * 50

$totalScore = $toolsOk + $envOk + $pythonOk + $mlOk + $gpuOk
$maxScore = 15

if (-not $Quick) {
    $totalScore += $mcpOk + $actionsOk + $structureOk
    $maxScore += 10
}

Write-Host "Overall Score: $totalScore / $maxScore" -ForegroundColor $(
    if ($totalScore -ge ($maxScore * 0.8)) { "Green" } 
    elseif ($totalScore -ge ($maxScore * 0.6)) { "Yellow" }
    else { "Red" }
)

if ($totalScore -ge ($maxScore * 0.8)) {
    Write-Success "Environment is well configured for ML workstation automation!"
} elseif ($totalScore -ge ($maxScore * 0.6)) {
    Write-Warning "Environment is partially configured. Address warnings above."
} else {
    Write-Error "Environment needs significant setup. Address errors above."
}

Write-Step "Next Steps"
if ($totalScore -lt ($maxScore * 0.8)) {
    Write-Host "1. Address any errors or warnings shown above" -ForegroundColor White
    Write-Host "2. Run setup scripts in the scripts/ directory" -ForegroundColor White
    Write-Host "3. Check docs\Automation_Runbook.md for detailed setup" -ForegroundColor White
}
Write-Host "4. Run full automation: .\scripts\run_end_to_end.ps1" -ForegroundColor White
Write-Host "5. Test workflows: .\scripts\trigger_workflows.ps1" -ForegroundColor White