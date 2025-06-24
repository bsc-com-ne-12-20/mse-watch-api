# MSE Cache Refresh - PowerShell Script
# Better for Windows Task Scheduler with proper error handling and logging

param(
    [switch]$Priority,
    [switch]$DryRun,
    [string]$LogPath = "cache_refresh_logs"
)

# Configuration
$ScriptDir = "c:\Users\innow\OneDrive\Desktop\mse_api"
$LogDir = Join-Path $ScriptDir $LogPath
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "refresh_$Timestamp.log"

# Ensure log directory exists
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Function to write log with timestamp
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

try {
    Write-Log "Starting MSE cache refresh process"
    Write-Log "Working directory: $ScriptDir"
    Write-Log "Log file: $LogFile"
    
    # Change to script directory
    Set-Location $ScriptDir
    
    # Check if Python script exists
    $PythonScript = if ($Priority) { "refresh_cache.py" } else { "daily_cache_refresh.py" }
    
    if (!(Test-Path $PythonScript)) {
        throw "Python script not found: $PythonScript"
    }
    
    # Build command arguments
    $Arguments = @()
    if ($Priority) {
        $Arguments += "--priority"
    }
    if ($DryRun) {
        $Arguments += "--dry-run"
    }
    
    # Execute Python script
    Write-Log "Executing: python $PythonScript $($Arguments -join ' ')"
    
    $Process = Start-Process -FilePath "python" -ArgumentList ($PythonScript, $Arguments) -Wait -PassThru -NoNewWindow
    
    if ($Process.ExitCode -eq 0) {
        Write-Log "Cache refresh completed successfully" "SUCCESS"
        exit 0
    } else {
        Write-Log "Cache refresh failed with exit code: $($Process.ExitCode)" "ERROR"
        exit $Process.ExitCode
    }
    
} catch {
    Write-Log "Fatal error: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}
