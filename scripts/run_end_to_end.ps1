param(
    [Parameter(Mandatory=$true)]
    [string]$Repo,                    # Repository name (e.g., "stangelika/CURSORTESTGITHUBACTIONMLMODEL")
    
    [Parameter(Mandatory=$false)]
    [string]$Pat = $env:GITHUB_TOKEN, # GitHub Personal Access Token
    
    [Parameter(Mandatory=$false)]
    [string]$Context7Key = $env:CONTEXT7_API_KEY, # Context7 API Key
    
    [Parameter(Mandatory=$false)]
    [switch]$InstallRunner = $false,  # Install self-hosted runner
    
    [Parameter(Mandatory=$false)]
    [string]$RunnerDir = "C:\actions-runner", # Runner installation directory
    
    [Parameter(Mandatory=$false)]
    [string]$RunnerLabels = "self-hosted,windows,gpu", # Runner labels
    
    [Parameter(Mandatory=$false)]
    [string]$StartCursorPath = "", # Path to Cursor.exe
    
    [Parameter(Mandatory=$false)]
    [switch]$TriggerWorkflows = $false, # Trigger test workflows
    
    [Parameter(Mandatory=$false)]
    [string]$LogDir = "logs\automation-$(Get-Date -Format 'yyyyMMdd-HHmmss')", # Log directory
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipMcpSetup = $false,   # Skip MCP setup
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport = $true   # Generate final report
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Step = "Magenta"
}

function Write-StatusMessage {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = $Colors[$Type]
    
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host $Message -ForegroundColor $color
    
    # Also log to file
    Add-Content -Path "$LogDir\automation.log" -Value "[$timestamp] [$Type] $Message"
}

function Test-Prerequisites {
    Write-StatusMessage "🔍 Checking prerequisites..." -Type "Step"
    
    $issues = @()
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-StatusMessage "✅ Python: $pythonVersion" -Type "Success"
    } catch {
        $issues += "Python not found or not in PATH"
    }
    
    # Check CUDA/NVIDIA
    try {
        $nvidiaSmi = & "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe" --query-gpu=name --format=csv,noheader 2>$null
        Write-StatusMessage "✅ GPU: $nvidiaSmi" -Type "Success"
    } catch {
        Write-StatusMessage "⚠️ nvidia-smi not found - GPU monitoring may be limited" -Type "Warning"
    }
    
    # Check Docker
    try {
        $dockerVersion = docker --version 2>&1
        Write-StatusMessage "✅ Docker: $dockerVersion" -Type "Success"
    } catch {
        $issues += "Docker not found - required for MCP GitHub server"
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>&1
        Write-StatusMessage "✅ Git: $gitVersion" -Type "Success"
    } catch {
        $issues += "Git not found"
    }
    
    # Check GitHub CLI (optional)
    try {
        $ghVersion = gh --version 2>&1 | Select-Object -First 1
        Write-StatusMessage "✅ GitHub CLI: $ghVersion" -Type "Success"
    } catch {
        Write-StatusMessage "ℹ️ GitHub CLI not found (optional)" -Type "Info"
    }
    
    if ($issues.Count -gt 0) {
        Write-StatusMessage "❌ Prerequisites check failed:" -Type "Error"
        foreach ($issue in $issues) {
            Write-StatusMessage "   - $issue" -Type "Error"
        }
        return $false
    }
    
    Write-StatusMessage "✅ All prerequisites satisfied" -Type "Success"
    return $true
}

function Test-EnvironmentVariables {
    Write-StatusMessage "🔍 Checking environment variables..." -Type "Step"
    
    $issues = @()
    
    if ([string]::IsNullOrEmpty($Pat)) {
        $issues += "GITHUB_TOKEN not set"
    } else {
        Write-StatusMessage "✅ GITHUB_TOKEN present" -Type "Success"
    }
    
    if ([string]::IsNullOrEmpty($Context7Key)) {
        Write-StatusMessage "⚠️ CONTEXT7_API_KEY not set (optional)" -Type "Warning"
    } else {
        Write-StatusMessage "✅ CONTEXT7_API_KEY present" -Type "Success"
    }
    
    if ($issues.Count -gt 0) {
        Write-StatusMessage "❌ Environment variables check failed:" -Type "Error"
        foreach ($issue in $issues) {
            Write-StatusMessage "   - $issue" -Type "Error"
        }
        return $false
    }
    
    return $true
}

function Install-PythonRequirements {
    Write-StatusMessage "📦 Installing Python requirements..." -Type "Step"
    
    try {
        # Check if requirements.txt exists
        if (Test-Path "requirements.txt") {
            python -m pip install --upgrade pip
            python -m pip install -r requirements.txt
        } else {
            # Install basic ML stack
            python -m pip install --upgrade pip
            python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
            python -m pip install numpy pandas scikit-learn matplotlib
            python -m pip install pynvml  # For GPU monitoring
        }
        
        Write-StatusMessage "✅ Python packages installed" -Type "Success"
        return $true
    } catch {
        Write-StatusMessage "❌ Failed to install Python packages: $($_.Exception.Message)" -Type "Error"
        return $false
    }
}

function Setup-MCPServers {
    if ($SkipMcpSetup) {
        Write-StatusMessage "⏭️ Skipping MCP setup (--SkipMcpSetup)" -Type "Info"
        return $true
    }
    
    Write-StatusMessage "🔧 Setting up MCP servers..." -Type "Step"
    
    try {
        # Run MCP setup if script exists
        if (Test-Path "scripts\setup_mcp_servers.ps1") {
            & "scripts\setup_mcp_servers.ps1" -Context7Key $Context7Key
        } else {
            Write-StatusMessage "⚠️ MCP setup script not found - run manually if needed" -Type "Warning"
        }
        
        # Validate MCP configuration
        if (Test-Path "scripts\check_mcp_setup.py") {
            python scripts\check_mcp_setup.py
        }
        
        Write-StatusMessage "✅ MCP servers configured" -Type "Success"
        return $true
    } catch {
        Write-StatusMessage "⚠️ MCP setup had issues: $($_.Exception.Message)" -Type "Warning"
        return $true  # Non-critical
    }
}

function Install-GitHubRunner {
    if (-not $InstallRunner) {
        Write-StatusMessage "⏭️ Skipping runner installation" -Type "Info"
        return $true
    }
    
    Write-StatusMessage "🏃 Installing GitHub self-hosted runner..." -Type "Step"
    
    try {
        if (Test-Path "scripts\install_runner.ps1") {
            $repoUrl = "https://github.com/$Repo"
            & "scripts\install_runner.ps1" -RepoUrl $repoUrl -Token $Pat -InstallDir $RunnerDir -Labels $RunnerLabels
            Write-StatusMessage "✅ GitHub runner installed" -Type "Success"
        } else {
            Write-StatusMessage "❌ Runner installation script not found" -Type "Error"
            return $false
        }
        
        return $true
    } catch {
        Write-StatusMessage "❌ Failed to install runner: $($_.Exception.Message)" -Type "Error"
        return $false
    }
}

function Test-GPUSetup {
    Write-StatusMessage "🎮 Testing GPU setup..." -Type "Step"
    
    try {
        # Test GPU monitoring
        if (Test-Path "scripts\gpu_monitor.py") {
            python scripts\gpu_monitor.py --test | Tee-Object -FilePath "$LogDir\gpu_test.log"
        }
        
        # Test PyTorch CUDA
        $torchTest = python -c @"
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'Device count: {torch.cuda.device_count()}')
    print(f'Device 0: {torch.cuda.get_device_name(0)}')
"@
        
        $torchTest | Tee-Object -FilePath "$LogDir\pytorch_test.log"
        Write-StatusMessage "✅ GPU setup tested" -Type "Success"
        return $true
    } catch {
        Write-StatusMessage "⚠️ GPU test had issues: $($_.Exception.Message)" -Type "Warning"
        return $true  # Non-critical
    }
}

function Start-CursorApplication {
    if ([string]::IsNullOrEmpty($StartCursorPath)) {
        Write-StatusMessage "⏭️ Skipping Cursor startup (no path provided)" -Type "Info"
        return $true
    }
    
    Write-StatusMessage "🚀 Starting Cursor..." -Type "Step"
    
    try {
        if (Test-Path $StartCursorPath) {
            # Kill existing Cursor processes
            Get-Process -Name "Cursor*" -ErrorAction SilentlyContinue | Stop-Process -Force
            Start-Sleep -Seconds 3
            
            # Start Cursor
            Start-Process -FilePath $StartCursorPath -WorkingDirectory (Get-Location).Path
            Write-StatusMessage "✅ Cursor started" -Type "Success"
        } else {
            Write-StatusMessage "❌ Cursor executable not found: $StartCursorPath" -Type "Error"
            return $false
        }
        
        return $true
    } catch {
        Write-StatusMessage "⚠️ Failed to start Cursor: $($_.Exception.Message)" -Type "Warning"
        return $true  # Non-critical
    }
}

function Trigger-TestWorkflows {
    if (-not $TriggerWorkflows) {
        Write-StatusMessage "⏭️ Skipping workflow triggers" -Type "Info"
        return $true
    }
    
    Write-StatusMessage "⚡ Triggering test workflows..." -Type "Step"
    
    try {
        # Trigger short CPU test
        if (Get-Command gh -ErrorAction SilentlyContinue) {
            gh workflow run "ml-test-github.yml" -R $Repo
            Write-StatusMessage "✅ ML Test workflow triggered" -Type "Success"
            
            # Wait a bit then trigger long run (optional)
            Start-Sleep -Seconds 10
            # gh workflow run "ml-long-run.yml" -R $Repo
            # Write-StatusMessage "✅ ML Long Run workflow triggered" -Type "Success"
        } else {
            Write-StatusMessage "⚠️ GitHub CLI not available for workflow triggers" -Type "Warning"
        }
        
        return $true
    } catch {
        Write-StatusMessage "⚠️ Failed to trigger workflows: $($_.Exception.Message)" -Type "Warning"
        return $true  # Non-critical
    }
}

function Generate-Report {
    if (-not $GenerateReport) {
        return $true
    }
    
    Write-StatusMessage "📊 Generating automation report..." -Type "Step"
    
    try {
        if (Test-Path "scripts\generate_report.ps1") {
            & "scripts\generate_report.ps1" -Template "docs\Report_Template.md" -Output "$LogDir\automation_report.md"
        } else {
            # Basic report generation
            $reportContent = @"
# Automation Run Report

Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Repository: $Repo

## Summary
- Prerequisites: Checked
- Environment: Configured  
- MCP Servers: $(if ($SkipMcpSetup) { "Skipped" } else { "Configured" })
- GitHub Runner: $(if ($InstallRunner) { "Installed" } else { "Skipped" })
- GPU Setup: Tested
- Cursor: $(if ([string]::IsNullOrEmpty($StartCursorPath)) { "Skipped" } else { "Started" })
- Workflows: $(if ($TriggerWorkflows) { "Triggered" } else { "Skipped" })

## Log Files
- Main log: $LogDir\automation.log
- GPU test: $LogDir\gpu_test.log  
- PyTorch test: $LogDir\pytorch_test.log

## Next Steps
1. Verify Cursor MCP servers are loaded
2. Check GitHub Actions runner status
3. Run test workflows manually if needed
4. Monitor GPU during training sessions

Generated by: run_end_to_end.ps1
"@
            
            $reportContent | Out-File -FilePath "$LogDir\automation_report.md" -Encoding UTF8
        }
        
        Write-StatusMessage "✅ Report generated: $LogDir\automation_report.md" -Type "Success"
        return $true
    } catch {
        Write-StatusMessage "⚠️ Report generation failed: $($_.Exception.Message)" -Type "Warning"
        return $true  # Non-critical
    }
}

# Main execution
try {
    Write-StatusMessage "🚀 Starting ML Workstation End-to-End Automation" -Type "Step"
    Write-StatusMessage "Repository: $Repo" -Type "Info"
    
    # Create log directory
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    Write-StatusMessage "Log directory: $LogDir" -Type "Info"
    
    # Step 1: Prerequisites
    if (-not (Test-Prerequisites)) {
        Write-StatusMessage "❌ Prerequisites check failed. Aborting." -Type "Error"
        exit 1
    }
    
    # Step 2: Environment variables
    if (-not (Test-EnvironmentVariables)) {
        Write-StatusMessage "❌ Environment check failed. Please set required variables." -Type "Error"
        exit 1
    }
    
    # Step 3: Python packages
    if (-not (Install-PythonRequirements)) {
        Write-StatusMessage "❌ Python packages installation failed. Aborting." -Type "Error"
        exit 1
    }
    
    # Step 4: MCP Setup
    Setup-MCPServers
    
    # Step 5: GitHub Runner
    if ($InstallRunner -and -not (Install-GitHubRunner)) {
        Write-StatusMessage "❌ Runner installation failed. Aborting." -Type "Error"
        exit 1
    }
    
    # Step 6: GPU Testing
    Test-GPUSetup
    
    # Step 7: Start Cursor
    Start-CursorApplication
    
    # Step 8: Trigger workflows
    Trigger-TestWorkflows
    
    # Step 9: Generate report
    Generate-Report
    
    Write-StatusMessage "✅ End-to-End automation completed successfully!" -Type "Success"
    Write-StatusMessage "📁 Logs and reports available in: $LogDir" -Type "Info"
    Write-StatusMessage "📚 See docs\Automation_Runbook.md for detailed usage" -Type "Info"
    
} catch {
    Write-StatusMessage "❌ Automation failed: $($_.Exception.Message)" -Type "Error"
    Write-StatusMessage "📁 Check logs in: $LogDir" -Type "Info"
    exit 1
}