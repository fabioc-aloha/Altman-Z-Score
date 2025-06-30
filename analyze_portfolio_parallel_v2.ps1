# ===============================================================================
# Altman Z-Score Parallel Portfolio Analyzer (PowerShell)
# Multi-threaded analysis for large portfolios with progress tracking
# Compatible with PowerShell 5.1+ and PowerShell Core 6+
# ===============================================================================

<#
.SYNOPSIS
    Runs Altman Z-Score analysis on large portfolios using parallel processing.

.DESCRIPTION
    This script processes large lists of stock tickers in parallel using PowerShell jobs
    or ForEach-Object -Parallel (PS 7+) to maximize performance and reduce total analysis time.
    Supports portfolio files, individual tickers, and predefined sector portfolios.

.PARAMETER Tickers
    Array of individual ticker symbols to analyze.

.PARAMETER PortfolioFile
    Path to a text file containing ticker symbols (one per line, # for comments).

.PARAMETER Sector
    Predefined sector portfolio to analyze (technology, healthcare, financial, industrial, energy).

.PARAMETER MaxThreads
    Maximum number of parallel threads to use. Default: CPU core count.

.PARAMETER BatchSize
    Number of tickers to process per batch. Default: 5.

.PARAMETER Quarters
    Number of quarters for historical analysis. Default: 8.

.PARAMETER LogLevel
    Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: WARNING.

.PARAMETER OutputDir
    Base output directory for results. Default: "output".

.PARAMETER ClearCache
    Clear all cached data before starting analysis.

.PARAMETER DryRun
    Show what would be processed without actually running analysis.

.PARAMETER Timeout
    Timeout in minutes for individual ticker analysis. Default: 10.

.PARAMETER ContinueOnError
    Continue processing remaining tickers if some fail.

.PARAMETER ShowProgress
    Show detailed progress information.

.PARAMETER Help
    Display comprehensive help information and usage examples.

.EXAMPLE
    .\analyze_portfolio_parallel_v2.ps1 -Tickers @("AAPL", "MSFT", "GOOGL")
    Analyzes specific tickers in parallel.

.EXAMPLE
    .\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\technology_portfolio.txt" -MaxThreads 8
    Analyzes portfolio file using 8 parallel threads.

.EXAMPLE
    .\analyze_portfolio_parallel_v2.ps1 -Sector technology -BatchSize 10 -Quarters 12
    Analyzes technology sector with larger batches and extended history.
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    [string[]]$Tickers = @(),
    [string]$PortfolioFile = "",
    [ValidateSet("technology", "healthcare", "financial", "industrial", "energy")]
    [string]$Sector = "",
    [int]$MaxThreads = 0,
    [int]$BatchSize = 5,
    [int]$Quarters = 8,
    [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")]
    [string]$LogLevel = "WARNING",
    [string]$OutputDir = "output",
    [switch]$ClearCache,
    [switch]$DryRun,
    [int]$Timeout = 10,
    [switch]$ContinueOnError,
    [switch]$ShowProgress,
    [switch]$Help
)

# Set error action preference
$ErrorActionPreference = "Continue"

# Set default values for switch parameters that should default to $true
if (-not $PSBoundParameters.ContainsKey('ContinueOnError')) {
    $ContinueOnError = $true
}
if (-not $PSBoundParameters.ContainsKey('ShowProgress')) {
    $ShowProgress = $true
}

# Initialize Python command variable
$script:PythonCommand = "python"

# Auto-detect max threads if not specified
if ($MaxThreads -eq 0) {
    $MaxThreads = (Get-CimInstance -ClassName Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
    if ($MaxThreads -eq 0) { $MaxThreads = 4 }  # Fallback
}

# Define colors for output
$Colors = @{
    Header   = "Cyan"
    Success  = "Green"
    Error    = "Red"
    Warning  = "Yellow"
    Info     = "White"
    Emphasis = "Magenta"
    Progress = "Blue"
}

# Global counters for thread-safe operations
$script:CompletedCount = 0
$script:SuccessCount = 0
$script:ErrorCount = 0
$script:TotalTickers = 0
$script:StartTime = Get-Date

function Write-ColorText {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

function Write-Header {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title
    )
    
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor $Colors.Header
    Write-Host (" " * ((80 - $Title.Length) / 2)) + $Title -ForegroundColor $Colors.Header
    Write-Host ("=" * 80) -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Section {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title
    )
    
    Write-Host ""
    Write-Host ("-" * 80) -ForegroundColor $Colors.Info
    Write-Host $Title -ForegroundColor $Colors.Emphasis
    Write-Host ("-" * 80) -ForegroundColor $Colors.Info
}

function Test-PythonAvailable {
    [CmdletBinding()]
    [OutputType([bool])]
    param()
    
    $pythonCommands = @('python', 'python3', 'py')
    
    foreach ($cmd in $pythonCommands) {
        try {
            $result = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✅ Python detected ($cmd): $result" "Success"
                $script:PythonCommand = $cmd
                return $true
            }
        }
        catch {
            # Expected behavior when command not found - continue silently
            Write-Verbose "Python command '$cmd' not found: $($_.Exception.Message)"
            continue
        }
    }
    
    Write-ColorText "❌ Python not found. Tried: $($pythonCommands -join ', ')" "Error"
    return $false
}

function Get-TickersFromFile {
    [CmdletBinding()]
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory)]
        [string]$FilePath
    )
    
    if (-not (Test-Path $FilePath)) {
        throw "Portfolio file not found: $FilePath"
    }
    
    $tickerList = [System.Collections.ArrayList]::new()
    
    try {
        $content = Get-Content $FilePath -ErrorAction Stop
        
        foreach ($line in $content) {
            $line = $line.Trim()
            # Skip empty lines and comments
            if ($line -and -not $line.StartsWith('#')) {
                # Extract ticker symbols (alphanumeric + dots for international)
                if ($line -match '^[A-Z0-9]+(\.[A-Z]+)?$|^[0-9]{6}\.[A-Z]{2}$') {
                    [void]$tickerList.Add($line)
                }
            }
        }
    }
    catch {
        throw "Error reading portfolio file '$FilePath': $($_.Exception.Message)"
    }
    
    return $tickerList.ToArray()
}

function Get-SectorTickers {
    [CmdletBinding()]
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory)]
        [string]$SectorName
    )
    
    $sectorFiles = @{
        "technology" = "portfolios\technology_growth_portfolio.txt"
        "healthcare" = "portfolios\altman_original_portfolio.txt"  # Contains some healthcare
        "financial"  = "portfolios\financial_institutions_portfolio.txt"
        "industrial" = "portfolios\altman_original_portfolio.txt"  # Contains industrials
        "energy"     = "portfolios\altman_original_portfolio.txt"  # Contains some energy
    }
    
    $filePath = $sectorFiles[$SectorName]
    if (-not $filePath -or -not (Test-Path $filePath)) {
        # Fallback to comprehensive portfolio and filter by sector
        $filePath = "portfolios\comprehensive_model_portfolio_cleaned.txt"
        if (-not (Test-Path $filePath)) {
            throw "No portfolio file found for sector: $SectorName"
        }
    }
    
    return Get-TickersFromFile $filePath
}

function Invoke-TickerAnalysis {
    [CmdletBinding()]
    [OutputType([hashtable])]
    param(
        [Parameter(Mandatory)]
        [string]$Ticker,
        [Parameter(Mandatory)]
        [int]$Quarters,
        [Parameter(Mandatory)]
        [string]$LogLevel,
        [Parameter(Mandatory)]
        [string]$OutputDir,
        [Parameter(Mandatory)]
        [int]$TimeoutMinutes
    )
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        # Create a process with timeout
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $script:PythonCommand
        $psi.Arguments = "main.py $Ticker --quarters $Quarters --log-level $LogLevel --progress never"
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $psi
        $process.Start() | Out-Null
        
        # Wait for completion with timeout
        $completed = $process.WaitForExit($TimeoutMinutes * 60 * 1000)
        
        $stopwatch.Stop()
        $duration = $stopwatch.Elapsed.TotalSeconds
        
        if (-not $completed) {
            $process.Kill()
            return @{
                Ticker   = $Ticker
                Success  = $false
                Duration = $duration
                Error    = "Timeout after $TimeoutMinutes minutes"
                Output   = ""
            }
        }
        
        $output = $process.StandardOutput.ReadToEnd()
        $errorOutput = $process.StandardError.ReadToEnd()
        $exitCode = $process.ExitCode
        
        return @{
            Ticker   = $Ticker
            Success  = ($exitCode -eq 0)
            Duration = $duration
            Error    = if ($exitCode -ne 0) { $errorOutput } else { "" }
            Output   = $output
        }
    }
    catch {
        Write-Error "Failed to analyze ticker '$Ticker': $($_.Exception.Message)"
        return @{
            Ticker   = $Ticker
            Success  = $false
            Duration = 0
            Error    = $_.Exception.Message
            Output   = ""
        }
    }
}

function Update-Progress {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Ticker,
        [Parameter(Mandatory)]
        [bool]$Success,
        [Parameter(Mandatory)]
        [double]$Duration,
        [string]$ErrorMessage = ""
    )
    
    # Thread-safe counter updates
    $script:CompletedCount++
    if ($Success) {
        $script:SuccessCount++
    }
    else {
        $script:ErrorCount++
    }
    
    $elapsed = (Get-Date) - $script:StartTime
    $rate = if ($elapsed.TotalMinutes -gt 0) { $script:CompletedCount / $elapsed.TotalMinutes } else { 0 }
    $eta = if ($rate -gt 0) { ($script:TotalTickers - $script:CompletedCount) / $rate } else { 0 }
    
    $percentage = [math]::Round(($script:CompletedCount / $script:TotalTickers) * 100, 1)
    
    if ($ShowProgress) {
        $status = if ($Success) { "✅" } else { "❌" }
        $durationText = "$([math]::Round($Duration, 1))s"
        
        $progressColor = if ($Success) { $Colors.Success } else { $Colors.Error }
        Write-Host "[$script:CompletedCount/$script:TotalTickers] $status $Ticker ($durationText) - $percentage% | ETA: $([math]::Round($eta, 1))m" -ForegroundColor $progressColor
        
        if (-not $Success -and $ErrorMessage) {
            Write-Host "    Error: $ErrorMessage" -ForegroundColor $Colors.Warning
        }
    }
}

function Start-ParallelAnalysis {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$TickerList,
        [Parameter(Mandatory)]
        [int]$MaxThreads,
        [Parameter(Mandatory)]
        [int]$BatchSize,
        [Parameter(Mandatory)]
        [hashtable]$Parameters
    )
    
    Write-ColorText "🚀 Starting parallel analysis with $MaxThreads threads..." "Info"
    Write-ColorText "📊 Processing $($TickerList.Count) tickers in batches of $BatchSize" "Info"
    Write-Host ""
    
    # Check PowerShell version for parallel support
    $useModernParallel = $PSVersionTable.PSVersion.Major -ge 7
    
    if ($useModernParallel) {
        Write-ColorText "🔄 Using PowerShell 7+ ForEach-Object -Parallel" "Info"
        
        $results = $TickerList | ForEach-Object -Parallel {
            $ticker = $_
            $params = $using:Parameters
            $pythonCmd = $using:script:PythonCommand
            
            # Import the function into the parallel session
            function Invoke-TickerAnalysis {
                [CmdletBinding()]
                [OutputType([hashtable])]
                param(
                    [Parameter(Mandatory)]
                    [string]$Ticker,
                    [Parameter(Mandatory)]
                    [int]$Quarters,
                    [Parameter(Mandatory)]
                    [string]$LogLevel,
                    [Parameter(Mandatory)]
                    [string]$OutputDir,
                    [Parameter(Mandatory)]
                    [int]$TimeoutMinutes
                )
                
                try {
                    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
                    
                    $psi = New-Object System.Diagnostics.ProcessStartInfo
                    $psi.FileName = $pythonCmd
                    $psi.Arguments = "main.py $Ticker --quarters $($params.Quarters) --log-level $($params.LogLevel) --progress never"
                    $psi.RedirectStandardOutput = $true
                    $psi.RedirectStandardError = $true
                    $psi.UseShellExecute = $false
                    $psi.CreateNoWindow = $true
                    
                    $process = New-Object System.Diagnostics.Process
                    $process.StartInfo = $psi
                    $process.Start() | Out-Null
                    
                    $completed = $process.WaitForExit($TimeoutMinutes * 60 * 1000)
                    
                    $stopwatch.Stop()
                    $duration = $stopwatch.Elapsed.TotalSeconds
                    
                    if (-not $completed) {
                        $process.Kill()
                        return @{
                            Ticker   = $Ticker
                            Success  = $false
                            Duration = $duration
                            Error    = "Timeout after $TimeoutMinutes minutes"
                        }
                    }
                    
                    # We only need stderr for error reporting, stdout not used
                    $process.StandardOutput.ReadToEnd() | Out-Null
                    $errorOutput = $process.StandardError.ReadToEnd()
                    $exitCode = $process.ExitCode
                    
                    return @{
                        Ticker   = $Ticker
                        Success  = ($exitCode -eq 0)
                        Duration = $duration
                        Error    = if ($exitCode -ne 0) { $errorOutput } else { "" }
                    }
                }
                catch {
                    return @{
                        Ticker   = $Ticker
                        Success  = $false
                        Duration = 0
                        Error    = $_.Exception.Message
                    }
                }
            }
            
            $result = Invoke-TickerAnalysis -Ticker $ticker -Quarters $params.Quarters -LogLevel $params.LogLevel -OutputDir $params.OutputDir -TimeoutMinutes $params.Timeout
            
            # Return result for collection
            $result
            
        } -ThrottleLimit $MaxThreads
        
        # Process all results at once
        foreach ($result in $results) {
            Update-Progress -Ticker $result.Ticker -Success $result.Success -Duration $result.Duration -ErrorMessage $result.Error
        }
        
    }
    else {
        Write-ColorText "🔄 Using PowerShell Jobs (Legacy Mode)" "Info"
        
        # Create batches for job processing
        $batches = [System.Collections.ArrayList]::new()
        for ($i = 0; $i -lt $TickerList.Count; $i += $BatchSize) {
            $end = [Math]::Min($i + $BatchSize - 1, $TickerList.Count - 1)
            [void]$batches.Add(@($TickerList[$i..$end]))
        }
        
        Write-ColorText "📦 Created $($batches.Count) batches" "Info"
        
        # Process batches with job management
        $jobs = [System.Collections.ArrayList]::new()
        
        foreach ($batch in $batches) {
            # Wait if we have too many jobs running
            while ((Get-Job -State Running).Count -ge $MaxThreads) {
                Start-Sleep -Milliseconds 500
                
                # Check for completed jobs
                $completedJobs = Get-Job -State Completed
                foreach ($job in $completedJobs) {
                    try {
                        $results = Receive-Job $job -ErrorAction Stop
                        foreach ($result in $results) {
                            Update-Progress -Ticker $result.Ticker -Success $result.Success -Duration $result.Duration -ErrorMessage $result.Error
                        }
                    }
                    catch {
                        Write-Error "Error receiving job results: $($_.Exception.Message)"
                    }
                    finally {
                        Remove-Job $job
                    }
                }
            }
            
            # Start new job for this batch
            $job = Start-Job -ScriptBlock {
                param($BatchTickers, $PythonCmd, $Params)
                
                $results = [System.Collections.ArrayList]::new()
                foreach ($ticker in $BatchTickers) {
                    try {
                        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
                        
                        $psi = New-Object System.Diagnostics.ProcessStartInfo
                        $psi.FileName = $PythonCmd
                        $psi.Arguments = "main.py $ticker --quarters $($Params.Quarters) --log-level $($Params.LogLevel) --progress never"
                        $psi.RedirectStandardOutput = $true
                        $psi.RedirectStandardError = $true
                        $psi.UseShellExecute = $false
                        $psi.CreateNoWindow = $true
                        
                        $process = New-Object System.Diagnostics.Process
                        $process.StartInfo = $psi
                        $process.Start() | Out-Null
                        
                        $completed = $process.WaitForExit($Params.Timeout * 60 * 1000)
                        
                        $stopwatch.Stop()
                        $duration = $stopwatch.Elapsed.TotalSeconds
                        
                        if (-not $completed) {
                            $process.Kill()
                            [void]$results.Add(@{
                                Ticker   = $ticker
                                Success  = $false
                                Duration = $duration
                                Error    = "Timeout after $($Params.Timeout) minutes"
                            })
                            continue
                        }
                        
                        # We only need stderr for error reporting, stdout not used  
                        $process.StandardOutput.ReadToEnd() | Out-Null
                        $errorOutput = $process.StandardError.ReadToEnd()
                        $exitCode = $process.ExitCode
                        
                        [void]$results.Add(@{
                            Ticker   = $ticker
                            Success  = ($exitCode -eq 0)
                            Duration = $duration
                            Error    = if ($exitCode -ne 0) { $errorOutput } else { "" }
                        })
                    }
                    catch {
                        [void]$results.Add(@{
                            Ticker   = $ticker
                            Success  = $false
                            Duration = 0
                            Error    = $_.Exception.Message
                        })
                    }
                }
                
                return $results.ToArray()
            } -ArgumentList $batch, $script:PythonCommand, $Parameters
            
            [void]$jobs.Add($job)
        }
        
        # Wait for all remaining jobs to complete
        Write-ColorText "⏳ Waiting for remaining jobs to complete..." "Info"
        
        while ($jobs.Count -gt 0) {
            $completedJobs = $jobs | Where-Object { $_.State -eq 'Completed' -or $_.State -eq 'Failed' }
            
            foreach ($job in $completedJobs) {
                try {
                    $results = Receive-Job $job -ErrorAction Stop
                    foreach ($result in $results) {
                        Update-Progress -Ticker $result.Ticker -Success $result.Success -Duration $result.Duration -ErrorMessage $result.Error
                    }
                }
                catch {
                    Write-Error "Error receiving job results: $($_.Exception.Message)"
                }
                finally {
                    Remove-Job $job
                    $jobs = $jobs | Where-Object { $_.Id -ne $job.Id }
                }
            }
            
            if ($jobs.Count -gt 0) {
                Start-Sleep -Milliseconds 1000
            }
        }
    }
}

function Show-Help {
    [CmdletBinding()]
    param()
    
    $helpText = @"

===============================================================================
                    ALTMAN Z-SCORE PARALLEL PORTFOLIO ANALYZER
                              COMPREHENSIVE HELP GUIDE
===============================================================================

OVERVIEW:
    This script performs parallel Altman Z-Score analysis on stock portfolios,
    supporting large-scale processing with multi-threading for optimal performance.

BASIC USAGE:
    .\analyze_portfolio_parallel_v2.ps1 [PARAMETERS]

PARAMETERS:
    -Tickers <string[]>         Individual ticker symbols to analyze
                               Example: @("AAPL", "MSFT", "GOOGL")
    
    -PortfolioFile <string>     Path to portfolio file (one ticker per line)
                               Example: "portfolios\technology_portfolio.txt"
    
    -Sector <string>           Predefined sector portfolio
                               Values: technology, healthcare, financial, industrial, energy
    
    -MaxThreads <int>          Maximum parallel threads (default: CPU cores)
                               Example: 16
    
    -BatchSize <int>           Tickers per batch (default: 5)
                               Example: 10
    
    -Quarters <int>            Historical quarters to analyze (default: 8)
                               Example: 12
    
    -LogLevel <string>         Logging verbosity (default: WARNING)
                               Values: DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    -OutputDir <string>        Output directory (default: "output")
                               Example: "results"
    
    -Timeout <int>             Timeout per ticker in minutes (default: 10)
                               Example: 15
    
    -ClearCache               Clear all cached data before analysis
    -DryRun                   Show what would be processed without running
    -ContinueOnError          Continue if some tickers fail (default: enabled)
    -ShowProgress             Display detailed progress (default: enabled)

COMMON USAGE EXAMPLES:

    1. ANALYZE SPECIFIC TICKERS:
       .\analyze_portfolio_parallel_v2.ps1 -Tickers @("AAPL", "MSFT", "GOOGL", "AMZN")

    2. ANALYZE PORTFOLIO FILE:
       .\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_model_portfolio_cleaned.txt"

    3. ANALYZE SECTOR WITH CUSTOM SETTINGS:
       .\analyze_portfolio_parallel_v2.ps1 -Sector technology -MaxThreads 16 -BatchSize 10 -Quarters 12

    4. DRY RUN (PREVIEW ONLY):
       .\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\large_portfolio.txt" -DryRun

    5. HIGH-PERFORMANCE ANALYSIS:
       .\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_model_portfolio_cleaned.txt" -MaxThreads 32 -BatchSize 15 -Timeout 20

===============================================================================
                        Press any key to continue...
===============================================================================

"@

    Write-Host $helpText -ForegroundColor Cyan
    Read-Host
}

# Handle help request immediately after parameter processing
if ($Help) {
    Show-Help
    exit 0
}

# Main execution starts here
Clear-Host
Write-Header "Altman Z-Score Parallel Portfolio Analyzer v2"

Write-ColorText "🔧 Configuration:" "Info"
Write-ColorText "   Max Threads: $MaxThreads" "Info"
Write-ColorText "   Batch Size: $BatchSize" "Info"
Write-ColorText "   Quarters: $Quarters" "Info"
Write-ColorText "   Log Level: $LogLevel" "Info"
Write-ColorText "   Timeout: $Timeout minutes" "Info"
Write-ColorText "   Output Dir: $OutputDir" "Info"
Write-Host ""

# Check if Python is available
if (-not (Test-PythonAvailable)) {
    Write-ColorText "❌ Please ensure Python is installed and available in your PATH." "Error"
    exit 1
}

# Clear cache if requested
if ($ClearCache) {
    Write-ColorText "🗑️ Clearing cache..." "Info"
    try {
        & $script:PythonCommand main.py --clear-cache
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Cache cleared successfully" "Success"
        }
        else {
            Write-ColorText "⚠️ Cache clear returned non-zero exit code: $LASTEXITCODE" "Warning"
        }
    }
    catch {
        Write-ColorText "⚠️ Failed to clear cache: $($_.Exception.Message)" "Warning"
    }
    Write-Host ""
}

# Determine ticker list
$allTickers = @()

try {
    if ($Tickers.Count -gt 0) {
        $allTickers = $Tickers
        Write-ColorText "📋 Using provided ticker list ($($allTickers.Count) tickers)" "Info"
    }
    elseif ($PortfolioFile) {
        $allTickers = Get-TickersFromFile $PortfolioFile
        Write-ColorText "📁 Loaded $($allTickers.Count) tickers from: $PortfolioFile" "Info"
    }
    elseif ($Sector) {
        $allTickers = Get-SectorTickers $Sector
        Write-ColorText "🏢 Loaded $($allTickers.Count) tickers for sector: $Sector" "Info"
    }
    else {
        Write-ColorText "❌ No ticker source specified. Use -Tickers, -PortfolioFile, or -Sector." "Error"
        exit 1
    }
}
catch {
    Write-ColorText "❌ Error loading tickers: $($_.Exception.Message)" "Error"
    exit 1
}

if ($allTickers.Count -eq 0) {
    Write-ColorText "❌ No tickers found to process." "Error"
    exit 1
}

# Remove duplicates and validate
$uniqueTickers = $allTickers | Sort-Object -Unique
if ($uniqueTickers.Count -ne $allTickers.Count) {
    Write-ColorText "⚠️ Removed $($allTickers.Count - $uniqueTickers.Count) duplicate tickers" "Warning"
    $allTickers = $uniqueTickers
}

$script:TotalTickers = $allTickers.Count

Write-ColorText "🎯 Ready to process $($allTickers.Count) unique tickers" "Success"

# Show ticker list if small enough or in dry run
if ($allTickers.Count -le 20 -or $DryRun) {
    Write-ColorText "📋 Ticker List:" "Info"
    $allTickers | ForEach-Object { Write-Host "   • $_" -ForegroundColor $Colors.Info }
    Write-Host ""
}

if ($DryRun) {
    Write-ColorText "🔍 DRY RUN - No analysis will be performed" "Warning"
    Write-ColorText "📊 Would process $($allTickers.Count) tickers with $MaxThreads threads" "Info"
    exit 0
}

# Confirm large portfolios
if ($allTickers.Count -gt 50) {
    Write-ColorText "⚠️ Large portfolio detected ($($allTickers.Count) tickers)" "Warning"
    $estimated = ($allTickers.Count * 30) / $MaxThreads / 60  # Rough estimate: 30s per ticker
    Write-ColorText "🕐 Estimated completion time: $([math]::Round($estimated, 1)) minutes" "Info"
    
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-ColorText "❌ Analysis cancelled by user." "Warning"
        exit 0
    }
}

# Create parameters hashtable for parallel execution
$parameters = @{
    Quarters  = $Quarters
    LogLevel  = $LogLevel
    OutputDir = $OutputDir
    Timeout   = $Timeout
}

# Start parallel analysis
Write-Section "Portfolio Analysis"

$script:StartTime = Get-Date

try {
    Start-ParallelAnalysis -TickerList $allTickers -MaxThreads $MaxThreads -BatchSize $BatchSize -Parameters $parameters
}
catch {
    Write-ColorText "❌ Critical error during parallel execution: $($_.Exception.Message)" "Error"
    exit 1
}

# Generate final summary
$endTime = Get-Date
$totalDuration = ($endTime - $script:StartTime).TotalMinutes

Write-Section "Analysis Complete"

Write-ColorText "📊 Final Results:" "Info"
Write-ColorText "   Total Processed: $script:CompletedCount" "Info"
Write-ColorText "   Successful: $script:SuccessCount" "Success"
Write-ColorText "   Failed: $script:ErrorCount" "Error"
Write-ColorText "   Success Rate: $([math]::Round(($script:SuccessCount / $script:CompletedCount) * 100, 1))%" "Info"
Write-ColorText "   Total Time: $([math]::Round($totalDuration, 2)) minutes" "Info"
Write-ColorText "   Average Rate: $([math]::Round($script:CompletedCount / $totalDuration, 1)) tickers/minute" "Info"

Write-Host ""

if ($script:SuccessCount -gt 0) {
    Write-ColorText "✅ Analysis completed! Check the output directory for results:" "Success"
    Write-ColorText "   📁 $OutputDir/" "Info"
    
    # List some output directories
    if (Test-Path $OutputDir) {
        $outputDirs = Get-ChildItem $OutputDir -Directory | Select-Object -First 5
        foreach ($dir in $outputDirs) {
            Write-ColorText "   📂 $($dir.Name)" "Info"
        }
        if ((Get-ChildItem $OutputDir -Directory).Count -gt 5) {
            Write-ColorText "   ... and $((Get-ChildItem $OutputDir -Directory).Count - 5) more" "Info"
        }
    }
}

if ($script:ErrorCount -gt 0) {
    Write-ColorText "⚠️ Some tickers failed to process. Check logs for details." "Warning"
}

Write-Host ""
Write-Header "Portfolio Analysis Complete"

# Return appropriate exit code
exit $(if ($script:ErrorCount -eq 0) { 0 } else { 1 })
