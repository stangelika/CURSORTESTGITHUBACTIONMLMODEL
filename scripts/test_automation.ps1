param(
    [Parameter(Mandatory=$false)]
    [switch]$SkipInteractive = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$QuickTest = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$LogDir = "logs\test-automation-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
)

$ErrorActionPreference = "Continue"

# Test results tracking
$TestResults = @{
    TotalTests = 0
    PassedTests = 0
    FailedTests = 0
    SkippedTests = 0
    Tests = @()
}

function Write-TestStep {
    param([string]$Message)
    Write-Host "🧪 $Message" -ForegroundColor Magenta
}

function Write-TestResult {
    param(
        [string]$TestName,
        [string]$Result,  # PASS, FAIL, SKIP
        [string]$Message = ""
    )
    
    $TestResults.TotalTests++
    $TestResults.Tests += @{
        Name = $TestName
        Result = $Result
        Message = $Message
        Timestamp = Get-Date
    }
    
    switch ($Result) {
        "PASS" { 
            $TestResults.PassedTests++
            Write-Host "✅ PASS: $TestName" -ForegroundColor Green
            if ($Message) { Write-Host "   $Message" -ForegroundColor Gray }
        }
        "FAIL" { 
            $TestResults.FailedTests++
            Write-Host "❌ FAIL: $TestName" -ForegroundColor Red
            if ($Message) { Write-Host "   $Message" -ForegroundColor Yellow }
        }
        "SKIP" { 
            $TestResults.SkippedTests++
            Write-Host "⏭️ SKIP: $TestName" -ForegroundColor Yellow
            if ($Message) { Write-Host "   $Message" -ForegroundColor Gray }
        }
    }
}

function Test-FileExists {
    param([string]$Path, [string]$TestName)
    
    if (Test-Path $Path) {
        Write-TestResult -TestName $TestName -Result "PASS" -Message "File exists: $Path"
        return $true
    } else {
        Write-TestResult -TestName $TestName -Result "FAIL" -Message "File missing: $Path"
        return $false
    }
}

function Test-CommandAvailable {
    param([string]$Command, [string]$TestName)
    
    try {
        $version = Invoke-Expression "$Command --version" 2>&1
        Write-TestResult -TestName $TestName -Result "PASS" -Message "$($version | Select-Object -First 1)"
        return $true
    } catch {
        Write-TestResult -TestName $TestName -Result "FAIL" -Message "Command not found: $Command"
        return $false
    }
}

function Test-PythonScript {
    param([string]$Script, [string]$TestName, [string[]]$Args = @())
    
    try {
        if (Test-Path $Script) {
            $output = python $Script @Args 2>&1
            $exitCode = $LASTEXITCODE
            
            if ($exitCode -eq 0) {
                Write-TestResult -TestName $TestName -Result "PASS" -Message "Script executed successfully"
                return $true
            } else {
                Write-TestResult -TestName $TestName -Result "FAIL" -Message "Script failed with exit code: $exitCode"
                return $false
            }
        } else {
            Write-TestResult -TestName $TestName -Result "FAIL" -Message "Script not found: $Script"
            return $false
        }
    } catch {
        Write-TestResult -TestName $TestName -Result "FAIL" -Message "Exception: $($_.Exception.Message)"
        return $false
    }
}

# Create log directory
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-TestStep "ML Workstation Automation Stack Test Suite"
Write-Host "Log directory: $LogDir" -ForegroundColor Gray
Write-Host "=" * 60

# Test 1: File Structure
Write-TestStep "Testing file structure..."

$requiredFiles = @(
    "docs\Automation_Runbook.md",
    "docs\Report_Template.md",
    "scripts\run_end_to_end.ps1",
    "scripts\setup_mcp_servers.ps1",
    "scripts\generate_report.ps1", 
    "scripts\cleanup_logs.ps1",
    "scripts\restart_cursor.ps1",
    "scripts\trigger_workflows.ps1",
    "scripts\verify_environment.ps1",
    "scripts\gpu_monitor.py",
    "experiments\train.py",
    ".github\workflows\ml-test-github.yml",
    ".github\workflows\ml-long-run.yml",
    "requirements_automation.txt"
)

foreach ($file in $requiredFiles) {
    Test-FileExists -Path $file -TestName "File: $file"
}

# Test 2: Core Tools
Write-TestStep "Testing core tools..."

Test-CommandAvailable -Command "python" -TestName "Python"
Test-CommandAvailable -Command "git" -TestName "Git"
Test-CommandAvailable -Command "docker" -TestName "Docker"

# Optional tools
try { Test-CommandAvailable -Command "gh" -TestName "GitHub CLI" } catch { Write-TestResult -TestName "GitHub CLI" -Result "SKIP" -Message "Optional tool" }
try { Test-CommandAvailable -Command "node" -TestName "Node.js" } catch { Write-TestResult -TestName "Node.js" -Result "SKIP" -Message "Optional tool" }

# Test 3: Environment Variables
Write-TestStep "Testing environment variables..."

if ($env:GITHUB_TOKEN) {
    Write-TestResult -TestName "GITHUB_TOKEN" -Result "PASS" -Message "Set (length: $($env:GITHUB_TOKEN.Length))"
} else {
    Write-TestResult -TestName "GITHUB_TOKEN" -Result "FAIL" -Message "Environment variable not set"
}

if ($env:CONTEXT7_API_KEY) {
    Write-TestResult -TestName "CONTEXT7_API_KEY" -Result "PASS" -Message "Set (length: $($env:CONTEXT7_API_KEY.Length))"
} else {
    Write-TestResult -TestName "CONTEXT7_API_KEY" -Result "SKIP" -Message "Optional environment variable"
}

# Test 4: Python Dependencies
Write-TestStep "Testing Python dependencies..."

$pythonDeps = @("torch", "numpy", "pandas", "matplotlib")
foreach ($dep in $pythonDeps) {
    try {
        $version = python -c "import $dep; print($dep.__version__)" 2>$null
        if ($version) {
            Write-TestResult -TestName "Python: $dep" -Result "PASS" -Message "Version: $version"
        } else {
            Write-TestResult -TestName "Python: $dep" -Result "FAIL" -Message "Import failed"
        }
    } catch {
        Write-TestResult -TestName "Python: $dep" -Result "FAIL" -Message "Not available"
    }
}

# Test 5: GPU and CUDA
Write-TestStep "Testing GPU setup..."

# NVIDIA SMI test
try {
    $nvidiaSmi = & "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe" --query-gpu=name --format=csv,noheader 2>$null
    if ($nvidiaSmi) {
        Write-TestResult -TestName "nvidia-smi" -Result "PASS" -Message "$nvidiaSmi"
    } else {
        Write-TestResult -TestName "nvidia-smi" -Result "FAIL" -Message "Command failed"
    }
} catch {
    Write-TestResult -TestName "nvidia-smi" -Result "FAIL" -Message "Not found"
}

# PyTorch CUDA test
try {
    $cudaTest = python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
    if ($cudaTest -match "True") {
        Write-TestResult -TestName "PyTorch CUDA" -Result "PASS" -Message "$cudaTest"
    } else {
        Write-TestResult -TestName "PyTorch CUDA" -Result "FAIL" -Message "$cudaTest"
    }
} catch {
    Write-TestResult -TestName "PyTorch CUDA" -Result "FAIL" -Message "Test failed"
}

# Test 6: Python Scripts
Write-TestStep "Testing Python scripts..."

Test-PythonScript -Script "scripts\gpu_monitor.py" -TestName "GPU Monitor" -Args @("--test")

if (Test-Path "experiments\train.py") {
    if (-not $QuickTest) {
        # Test training script with minimal parameters
        Test-PythonScript -Script "experiments\train.py" -TestName "Training Script" -Args @("--epochs", "1", "--device", "cpu")
    } else {
        Write-TestResult -TestName "Training Script" -Result "SKIP" -Message "Skipped in quick test mode"
    }
}

# Test 7: PowerShell Scripts Syntax
Write-TestStep "Testing PowerShell scripts syntax..."

$psScripts = @(
    "scripts\run_end_to_end.ps1",
    "scripts\setup_mcp_servers.ps1",
    "scripts\generate_report.ps1",
    "scripts\cleanup_logs.ps1",
    "scripts\restart_cursor.ps1",
    "scripts\trigger_workflows.ps1",
    "scripts\verify_environment.ps1"
)

foreach ($script in $psScripts) {
    if (Test-Path $script) {
        try {
            # Test syntax by parsing the script
            $errors = $null
            [System.Management.Automation.PSParser]::Tokenize((Get-Content $script -Raw), [ref]$errors)
            
            if ($errors.Count -eq 0) {
                Write-TestResult -TestName "PS Syntax: $script" -Result "PASS" -Message "No syntax errors"
            } else {
                Write-TestResult -TestName "PS Syntax: $script" -Result "FAIL" -Message "$($errors.Count) syntax errors"
            }
        } catch {
            Write-TestResult -TestName "PS Syntax: $script" -Result "FAIL" -Message "Parse error: $($_.Exception.Message)"
        }
    }
}

# Test 8: GitHub Workflows Syntax
Write-TestStep "Testing GitHub workflow syntax..."

$workflows = Get-ChildItem -Path ".github\workflows" -Filter "*.yml" -ErrorAction SilentlyContinue
foreach ($workflow in $workflows) {
    try {
        # Basic YAML syntax check
        $content = Get-Content $workflow.FullName -Raw
        if ($content -match "name:" -and $content -match "on:" -and $content -match "jobs:") {
            Write-TestResult -TestName "Workflow: $($workflow.Name)" -Result "PASS" -Message "Basic structure valid"
        } else {
            Write-TestResult -TestName "Workflow: $($workflow.Name)" -Result "FAIL" -Message "Missing required sections"
        }
    } catch {
        Write-TestResult -TestName "Workflow: $($workflow.Name)" -Result "FAIL" -Message "Read error"
    }
}

# Test 9: Interactive Tests (if not skipped)
if (-not $SkipInteractive -and -not $QuickTest) {
    Write-TestStep "Interactive tests..."
    
    Write-Host "Press Enter to test verify_environment.ps1 script..." -ForegroundColor Yellow
    Read-Host
    
    try {
        & ".\scripts\verify_environment.ps1" -Quick
        Write-TestResult -TestName "Environment Verification" -Result "PASS" -Message "Script executed"
    } catch {
        Write-TestResult -TestName "Environment Verification" -Result "FAIL" -Message "Script failed"
    }
}

# Test 10: Documentation Quality
Write-TestStep "Testing documentation..."

$docs = @("docs\Automation_Runbook.md", "docs\Report_Template.md")
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        $content = Get-Content $doc -Raw
        $wordCount = ($content -split '\s+').Count
        
        if ($wordCount -gt 100) {
            Write-TestResult -TestName "Doc: $doc" -Result "PASS" -Message "$wordCount words"
        } else {
            Write-TestResult -TestName "Doc: $doc" -Result "FAIL" -Message "Too short: $wordCount words"
        }
    }
}

# Generate Test Report
Write-TestStep "Generating test report..."

$reportContent = @"
# ML Workstation Automation Test Report

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Test Suite: End-to-End Automation Validation

## Summary
- Total Tests: $($TestResults.TotalTests)
- Passed: $($TestResults.PassedTests) ✅
- Failed: $($TestResults.FailedTests) ❌  
- Skipped: $($TestResults.SkippedTests) ⏭️

Success Rate: $(if ($TestResults.TotalTests -gt 0) { [math]::Round(($TestResults.PassedTests / $TestResults.TotalTests) * 100, 1) } else { 0 })%

## Test Results

"@

foreach ($test in $TestResults.Tests) {
    $reportContent += "### $($test.Name)`n"
    $reportContent += "**Result:** $($test.Result)`n"
    if ($test.Message) {
        $reportContent += "**Details:** $($test.Message)`n"
    }
    $reportContent += "**Time:** $($test.Timestamp.ToString('HH:mm:ss'))`n`n"
}

$reportContent += @"

## Recommendations

Based on test results:
"@

if ($TestResults.FailedTests -gt 0) {
    $reportContent += "`n- ❌ Address $($TestResults.FailedTests) failed tests before proceeding"
}

if ($TestResults.SkippedTests -gt 0) {
    $reportContent += "`n- ⏭️ Consider addressing $($TestResults.SkippedTests) skipped tests for full functionality"
}

if ($TestResults.PassedTests -eq $TestResults.TotalTests) {
    $reportContent += "`n- ✅ All tests passed! The automation stack is ready for production use."
}

$reportPath = "$LogDir\test_report.md"
$reportContent | Out-File -FilePath $reportPath -Encoding UTF8

# Final Summary
Write-Host "`n" + "=" * 60
Write-TestStep "Test Suite Completed"

Write-Host "Total Tests: $($TestResults.TotalTests)" -ForegroundColor White
Write-Host "Passed: $($TestResults.PassedTests)" -ForegroundColor Green
Write-Host "Failed: $($TestResults.FailedTests)" -ForegroundColor Red
Write-Host "Skipped: $($TestResults.SkippedTests)" -ForegroundColor Yellow

$successRate = if ($TestResults.TotalTests -gt 0) { ($TestResults.PassedTests / $TestResults.TotalTests) * 100 } else { 0 }
Write-Host "Success Rate: $([math]::Round($successRate, 1))%" -ForegroundColor $(
    if ($successRate -ge 90) { "Green" }
    elseif ($successRate -ge 70) { "Yellow" }
    else { "Red" }
)

Write-Host "`nTest report saved: $reportPath" -ForegroundColor Cyan

if ($TestResults.FailedTests -eq 0) {
    Write-Host "`n🎉 All critical tests passed! The ML automation stack is ready." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ Some tests failed. Review the report and fix issues before deployment." -ForegroundColor Yellow
    exit 1
}