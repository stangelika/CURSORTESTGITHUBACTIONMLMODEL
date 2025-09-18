param(
    [Parameter(Mandatory=$false)]
    [string]$Workflow = "ml-test-github",  # or "ml-long-run" 
    
    [Parameter(Mandatory=$false)]
    [string]$Repo = "",
    
    [Parameter(Mandatory=$false)]
    [string]$RunName = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Wait = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$WaitMinutes = 10
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "⚡ $Message" -ForegroundColor Cyan
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

# Determine repository
if ([string]::IsNullOrEmpty($Repo)) {
    try {
        $remoteUrl = git remote get-url origin 2>$null
        $Repo = $remoteUrl -replace "\.git$", "" -replace ".*github\.com[:/]", ""
        Write-Step "Auto-detected repository: $Repo"
    } catch {
        Write-Error "Could not determine repository. Please specify with -Repo parameter."
        exit 1
    }
}

# Check GitHub CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) not found. Please install: https://cli.github.com/"
    exit 1
}

# Check authentication
try {
    $authStatus = gh auth status 2>&1
    Write-Step "GitHub CLI authenticated"
} catch {
    Write-Error "GitHub CLI not authenticated. Run: gh auth login"
    exit 1
}

# Validate workflow file exists
$workflowFile = ".github/workflows/$Workflow.yml"
if (-not (Test-Path $workflowFile)) {
    Write-Error "Workflow file not found: $workflowFile"
    
    Write-Step "Available workflows:"
    Get-ChildItem -Path ".github/workflows" -Filter "*.yml" | ForEach-Object {
        Write-Host "  - $($_.BaseName)" -ForegroundColor Gray
    }
    exit 1
}

Write-Step "Triggering workflow: $Workflow"
Write-Step "Repository: $Repo"
Write-Step "Workflow file: $workflowFile"

# Build command arguments
$ghArgs = @("workflow", "run", "$Workflow.yml", "--repo", $Repo)

# Add run name if specified
if (-not [string]::IsNullOrEmpty($RunName)) {
    $ghArgs += @("--field", "run_name=$RunName")
    Write-Step "Run name: $RunName"
}

try {
    # Trigger workflow
    Write-Step "Executing: gh $($ghArgs -join ' ')"
    & gh @ghArgs
    
    Write-Success "Workflow triggered successfully!"
    
    # Wait and monitor if requested
    if ($Wait) {
        Write-Step "Waiting for workflow to start (max $WaitMinutes minutes)..."
        
        $startTime = Get-Date
        $endTime = $startTime.AddMinutes($WaitMinutes)
        $found = $false
        
        while ((Get-Date) -lt $endTime -and -not $found) {
            Start-Sleep -Seconds 10
            
            try {
                $runs = gh run list --workflow="$Workflow.yml" --repo=$Repo --limit=1 --json=status,conclusion,displayTitle,url | ConvertFrom-Json
                
                if ($runs.Count -gt 0) {
                    $run = $runs[0]
                    $status = $run.status
                    $conclusion = $run.conclusion
                    $title = $run.displayTitle
                    $url = $run.url
                    
                    Write-Step "Latest run: $title"
                    Write-Step "Status: $status $(if ($conclusion) { "($conclusion)" })"
                    Write-Step "URL: $url"
                    
                    if ($status -eq "completed") {
                        if ($conclusion -eq "success") {
                            Write-Success "Workflow completed successfully!"
                        } elseif ($conclusion -eq "failure") {
                            Write-Error "Workflow failed!"
                        } else {
                            Write-Warning "Workflow completed with status: $conclusion"
                        }
                        $found = $true
                    } elseif ($status -eq "in_progress") {
                        Write-Step "Workflow is running..."
                    }
                }
            } catch {
                Write-Warning "Could not check workflow status: $($_.Exception.Message)"
            }
        }
        
        if (-not $found -and (Get-Date) -ge $endTime) {
            Write-Warning "Timeout waiting for workflow completion"
        }
    } else {
        # Just show the latest run info
        Start-Sleep -Seconds 5  # Give GitHub a moment to register the run
        
        try {
            $runs = gh run list --workflow="$Workflow.yml" --repo=$Repo --limit=1 --json=status,displayTitle,url | ConvertFrom-Json
            
            if ($runs.Count -gt 0) {
                $run = $runs[0]
                Write-Step "Monitor run at: $($run.url)"
            }
        } catch {
            Write-Step "Check workflow status at: https://github.com/$Repo/actions"
        }
    }
    
    # Show helpful commands
    Write-Step "Helpful commands:"
    Write-Host "  # List recent runs:" -ForegroundColor Gray
    Write-Host "  gh run list --repo=$Repo --limit=5" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  # View specific run logs:" -ForegroundColor Gray  
    Write-Host "  gh run view <run_id> --repo=$Repo --log" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  # Cancel a running workflow:" -ForegroundColor Gray
    Write-Host "  gh run cancel <run_id> --repo=$Repo" -ForegroundColor Gray
    
} catch {
    Write-Error "Failed to trigger workflow: $($_.Exception.Message)"
    
    Write-Step "Troubleshooting:"
    Write-Host "1. Check repository permissions" -ForegroundColor Gray
    Write-Host "2. Verify workflow file syntax" -ForegroundColor Gray  
    Write-Host "3. Ensure GitHub token has workflow permissions" -ForegroundColor Gray
    Write-Host "4. Try: gh workflow list --repo=$Repo" -ForegroundColor Gray
    
    exit 1
}