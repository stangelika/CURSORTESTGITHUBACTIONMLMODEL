param(
    [Parameter(Mandatory=$false)]
    [int]$DaysToKeep = 30,
    
    [Parameter(Mandatory=$false)]
    [string[]]$LogDirs = @("logs", "reports", "experiments\results"),
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeSystemLogs = $false
)

$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Message)
    Write-Host "🧹 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Format-FileSize {
    param([long]$Size)
    
    if ($Size -lt 1KB) { return "$Size B" }
    elseif ($Size -lt 1MB) { return "{0:N1} KB" -f ($Size / 1KB) }
    elseif ($Size -lt 1GB) { return "{0:N1} MB" -f ($Size / 1MB) }
    else { return "{0:N1} GB" -f ($Size / 1GB) }
}

Write-Step "Starting log cleanup (keeping files newer than $DaysToKeep days)"
if ($WhatIf) {
    Write-Warning "Running in WhatIf mode - no files will be deleted"
}

$cutoffDate = (Get-Date).AddDays(-$DaysToKeep)
$totalFilesProcessed = 0
$totalFilesDeleted = 0
$totalSizeFreed = 0

foreach ($logDir in $LogDirs) {
    if (-not (Test-Path $logDir)) {
        Write-Warning "Directory not found: $logDir"
        continue
    }
    
    Write-Step "Processing directory: $logDir"
    
    # Get old files
    $oldFiles = Get-ChildItem -Path $logDir -Recurse -File | Where-Object { 
        $_.LastWriteTime -lt $cutoffDate
    }
    
    $dirFilesDeleted = 0
    $dirSizeFreed = 0
    
    foreach ($file in $oldFiles) {
        $totalFilesProcessed++
        
        try {
            $fileSize = $file.Length
            $relativePath = $file.FullName -replace [regex]::Escape((Get-Location).Path + "\"), ""
            
            if ($WhatIf) {
                Write-Host "Would delete: $relativePath ($(Format-FileSize $fileSize), modified $(Get-Date $file.LastWriteTime -Format 'yyyy-MM-dd'))" -ForegroundColor Yellow
            } else {
                Remove-Item -Path $file.FullName -Force
                Write-Host "Deleted: $relativePath ($(Format-FileSize $fileSize))" -ForegroundColor Gray
            }
            
            $dirFilesDeleted++
            $dirSizeFreed += $fileSize
            $totalFilesDeleted++
            $totalSizeFreed += $fileSize
            
        } catch {
            Write-Warning "Failed to delete $($file.FullName): $($_.Exception.Message)"
        }
    }
    
    if ($dirFilesDeleted -gt 0) {
        Write-Success "Directory $logDir - Deleted: $dirFilesDeleted files, Freed: $(Format-FileSize $dirSizeFreed)"
    } else {
        Write-Step "Directory $logDir - No old files to clean"
    }
    
    # Clean empty subdirectories
    if (-not $WhatIf) {
        $emptyDirs = Get-ChildItem -Path $logDir -Recurse -Directory | 
                     Where-Object { (Get-ChildItem $_.FullName -Recurse -File | Measure-Object).Count -eq 0 } |
                     Sort-Object FullName -Descending
        
        foreach ($emptyDir in $emptyDirs) {
            try {
                Remove-Item -Path $emptyDir.FullName -Force
                Write-Host "Removed empty directory: $($emptyDir.Name)" -ForegroundColor Gray
            } catch {
                Write-Warning "Failed to remove empty directory $($emptyDir.FullName): $($_.Exception.Message)"
            }
        }
    }
}

# Additional cleanup tasks
Write-Step "Additional cleanup tasks..."

# Clean temporary Python files
$tempFiles = @("*.pyc", "__pycache__", "*.pyo", ".pytest_cache")
foreach ($pattern in $tempFiles) {
    $files = Get-ChildItem -Path . -Recurse -Name $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        try {
            if ($WhatIf) {
                Write-Host "Would delete temp file: $file" -ForegroundColor Yellow
            } else {
                Remove-Item -Path $file -Recurse -Force
                Write-Host "Deleted temp file: $file" -ForegroundColor Gray
            }
        } catch {
            Write-Warning "Failed to delete temp file $file: $($_.Exception.Message)"
        }
    }
}

# Clean old checkpoint files (keep only latest 5)
$checkpointDir = "experiments\models"
if (Test-Path $checkpointDir) {
    $checkpoints = Get-ChildItem -Path $checkpointDir -Filter "checkpoint_epoch_*.pth" | 
                   Sort-Object LastWriteTime -Descending
    
    if ($checkpoints.Count -gt 5) {
        $oldCheckpoints = $checkpoints | Select-Object -Skip 5
        foreach ($checkpoint in $oldCheckpoints) {
            try {
                if ($WhatIf) {
                    Write-Host "Would delete old checkpoint: $($checkpoint.Name) ($(Format-FileSize $checkpoint.Length))" -ForegroundColor Yellow
                } else {
                    Remove-Item -Path $checkpoint.FullName -Force
                    Write-Host "Deleted old checkpoint: $($checkpoint.Name) ($(Format-FileSize $checkpoint.Length))" -ForegroundColor Gray
                    $totalFilesDeleted++
                    $totalSizeFreed += $checkpoint.Length
                }
            } catch {
                Write-Warning "Failed to delete checkpoint $($checkpoint.FullName): $($_.Exception.Message)"
            }
        }
    }
}

# System logs (if requested)
if ($IncludeSystemLogs) {
    Write-Step "Cleaning system logs..."
    
    # Windows Event Logs (requires admin)
    try {
        $eventLogs = @("Application", "System", "Security")
        foreach ($logName in $eventLogs) {
            if ($WhatIf) {
                Write-Host "Would clear event log: $logName" -ForegroundColor Yellow
            } else {
                # Only clear if running as admin
                if (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
                    Clear-EventLog -LogName $logName -ErrorAction SilentlyContinue
                    Write-Host "Cleared event log: $logName" -ForegroundColor Gray
                } else {
                    Write-Warning "Administrator privileges required to clear event logs"
                }
            }
        }
    } catch {
        Write-Warning "Failed to clear event logs: $($_.Exception.Message)"
    }
    
    # Temporary folders
    $tempDirs = @($env:TEMP, "$env:LOCALAPPDATA\Temp")
    foreach ($tempDir in $tempDirs) {
        if (Test-Path $tempDir) {
            try {
                $tempFiles = Get-ChildItem -Path $tempDir -Recurse -File | 
                            Where-Object { $_.LastWriteTime -lt $cutoffDate }
                
                foreach ($tempFile in $tempFiles) {
                    try {
                        if ($WhatIf) {
                            Write-Host "Would delete temp: $($tempFile.Name)" -ForegroundColor Yellow  
                        } else {
                            Remove-Item -Path $tempFile.FullName -Force
                            $totalSizeFreed += $tempFile.Length
                        }
                    } catch {
                        # Ignore temp file deletion errors
                    }
                }
            } catch {
                Write-Warning "Could not process temp directory: $tempDir"
            }
        }
    }
}

# Summary
Write-Step "Cleanup Summary"
Write-Host "Files processed: $totalFilesProcessed" -ForegroundColor White
Write-Host "Files deleted: $totalFilesDeleted" -ForegroundColor White  
Write-Host "Space freed: $(Format-FileSize $totalSizeFreed)" -ForegroundColor White

if ($WhatIf) {
    Write-Warning "This was a dry run. Use without -WhatIf to actually delete files."
} else {
    Write-Success "Cleanup completed successfully!"
}

# Schedule reminder
Write-Step "💡 Tip: Schedule this script to run weekly with Task Scheduler:"
Write-Host "schtasks /create /tn 'ML Cleanup' /tr 'powershell.exe -File `"$(Resolve-Path $MyInvocation.MyCommand.Path)`" -DaysToKeep 30' /sc weekly" -ForegroundColor Gray