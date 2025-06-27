<#
.SYNOPSIS
    Run Altman Z-Score portfolio analysis with parallel processing

.DESCRIPTION
    Simple parallel processing script for portfolio analysis. Splits tickers into batches
    and runs them concurrently using PowerShell background jobs.

.PARAMETER PortfolioFile
    Path to the portfolio file containing ticker symbols (one per line, # comments ignored)

.PARAMETER ParallelProcesses
    Number of parallel processes to run (default: 8, recommended: 4-12)

.PARAMETER EnhancedAnalysis
    Enable enhanced analysis features for upgraded FMP accounts (default: true)

.PARAMETER Quarters
    Number of quarters for historical analysis (default: 12)

.PARAMETER Help
    Display help information and usage examples

.EXAMPLE
    .\run_parallel_portfolio.ps1 -Help

.EXAMPLE
    .\run_parallel_portfolio.ps1 -PortfolioFile "portfolios/my_portfolio.txt" -ParallelProcesses 4

.EXAMPLE
    .\run_parallel_portfolio.ps1 -PortfolioFile "portfolios/tech_portfolio.txt" -ParallelProcesses 6 -Quarters 12
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$PortfolioFile,
    
    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 16)]
    [int]$ParallelProcesses = 8,
    
    [Parameter(Mandatory = $false)]
    [bool]$EnhancedAnalysis = $true,
    
    [Parameter(Mandatory = $false)]
    [ValidateRange(4, 40)]
    [int]$Quarters = 12,
    
    [Parameter(Mandatory = $false)]
    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Show-Help {
    <#
    .SYNOPSIS
        Display help information for the parallel portfolio analysis script
    #>
    
    Write-Host "`nAltman Z-Score Parallel Portfolio Analysis" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    
    Write-Host "`nDESCRIPTION:" -ForegroundColor Yellow
    Write-Host "  Runs Altman Z-Score analysis on a portfolio of stocks using parallel processing."
    Write-Host "  Splits tickers into batches and processes them concurrently for faster analysis."
    
    Write-Host "`nUSAGE:" -ForegroundColor Yellow
    Write-Host "  .\run_parallel_portfolio.ps1 -PortfolioFile <file> [options]"
    
    Write-Host "`nREQUIRED PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -PortfolioFile <String>"
    Write-Host "      Path to portfolio file containing ticker symbols (one per line)"
    Write-Host "      Comments starting with # are ignored"
    
    Write-Host "`nOPTIONAL PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -ParallelProcesses <Int32>"
    Write-Host "      Number of parallel processes (1-16, default: 8)"
    Write-Host "      Recommended: 4-12 depending on system resources"
    
    Write-Host "  -EnhancedAnalysis"
    Write-Host "      Enable enhanced analysis features (default: true)"
    Write-Host "      Requires upgraded FMP account for full functionality"
    Write-Host "      Use -EnhancedAnalysis `$false to disable"
    
    Write-Host "  -Quarters <Int32>"
    Write-Host "      Number of quarters for historical analysis (4-40, default: 12)"
    Write-Host "      More quarters provide better trend analysis"
    
    Write-Host "  -Help"
    Write-Host "      Display this help information"
    
    Write-Host "`nEXAMPLES:" -ForegroundColor Yellow
    Write-Host "  # Default enhanced analysis (8 processes, 12 quarters, enhanced enabled)"
    Write-Host "  .\run_parallel_portfolio.ps1 -PortfolioFile 'portfolios/my_stocks.txt'"
    
    Write-Host "`n  # Conservative analysis for older systems"
    Write-Host "  .\run_parallel_portfolio.ps1 -PortfolioFile 'portfolios/sp500.txt' -ParallelProcesses 4"
    
    Write-Host "`n  # Maximum performance for large portfolios"
    Write-Host "  .\run_parallel_portfolio.ps1 -PortfolioFile 'portfolios/tech_stocks.txt' -ParallelProcesses 12 -Quarters 20"
    
    Write-Host "`n  # Basic analysis (disable enhanced features)"
    Write-Host "  .\run_parallel_portfolio.ps1 -PortfolioFile 'portfolios/large_portfolio.txt' -EnhancedAnalysis `$false -Quarters 4"
    
    Write-Host "`nPORTFOLIO FILE FORMAT:" -ForegroundColor Yellow
    Write-Host "  # Comments start with # and are ignored"
    Write-Host "  AAPL"
    Write-Host "  MSFT"
    Write-Host "  GOOGL"
    Write-Host "  # Technology stocks"
    Write-Host "  NVDA"
    Write-Host "  AMD"
    
    Write-Host "`nOUTPUT:" -ForegroundColor Yellow
    Write-Host "  Results are saved to the 'output' folder with individual ticker subdirectories"
    Write-Host "  Each ticker gets: charts, reports, CSV data, and AI insights"
    
    Write-Host "`nPERFORMANCE TIPS:" -ForegroundColor Yellow
    Write-Host "  • Default settings (8 processes, 12 quarters, enhanced) are optimized for modern systems"
    Write-Host "  • Use 4-6 parallel processes for older or resource-constrained systems"
    Write-Host "  • Use 8-12 parallel processes for powerful systems with large portfolios"
    Write-Host "  • Monitor system resources to avoid overloading"
    Write-Host "  • Enhanced analysis provides significantly better insights but uses more API calls"
    
    Write-Host "`nFor more information, see the project documentation or run:"
    Write-Host "  Get-Help .\run_parallel_portfolio.ps1 -Full"
    Write-Host ""
}

function Get-Portfolio {
    param([string]$FilePath)
    
    Write-Host "Loading portfolio from: $FilePath" -ForegroundColor Cyan
    
    $content = Get-Content $FilePath -ErrorAction Stop
    $tickers = @()
    
    foreach ($line in $content) {
        $line = $line.Trim()
        if ($line -and !$line.StartsWith("#")) {
            $tickers += $line.ToUpper()
        }
    }
    
    if ($tickers.Count -eq 0) {
        throw "No valid tickers found in portfolio file"
    }
    
    Write-Host "Loaded $($tickers.Count) tickers: $($tickers -join ', ')" -ForegroundColor Green
    return $tickers
}

function Split-IntoOptimalBatches {
    param(
        [string[]]$Tickers,
        [int]$ProcessCount
    )
    
    $totalTickers = $Tickers.Count
    $baseSize = [Math]::Floor($totalTickers / $ProcessCount)
    $remainder = $totalTickers % $ProcessCount
    
    $batches = @()
    $currentIndex = 0
    
    for ($i = 0; $i -lt $ProcessCount; $i++) {
        if ($i -lt $remainder) {
            $batchSize = $baseSize + 1
        }
        else {
            $batchSize = $baseSize
        }
        
        if ($currentIndex -lt $totalTickers) {
            $endIndex = [Math]::Min($currentIndex + $batchSize - 1, $totalTickers - 1)
            $batch = $Tickers[$currentIndex..$endIndex]
            $batches += , $batch
            $currentIndex += $batchSize
        }
    }
    
    return $batches
}

# Main execution
try {
    # Check if help was requested or no parameters provided
    if ($Help -or (-not $PortfolioFile)) {
        Show-Help
        exit 0
    }
    
    Write-Host "`nAltman Z-Score Parallel Portfolio Analysis" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    
    # Load and validate portfolio
    $tickers = Get-Portfolio -FilePath $PortfolioFile
    
    # Split into batches
    $batches = Split-IntoOptimalBatches -Tickers $tickers -ProcessCount $ParallelProcesses
    $activeBatches = $batches | Where-Object { $_.Count -gt 0 }
    
    Write-Host "`nCreated $($activeBatches.Count) batches for parallel processing" -ForegroundColor Yellow
    for ($i = 0; $i -lt $activeBatches.Count; $i++) {
        $batch = $activeBatches[$i]
        Write-Host "  Batch $($i + 1): $($batch.Count) tickers - $($batch -join ', ')" -ForegroundColor Gray
    }
    
    # Start all batch jobs
    Write-Host "`nStarting parallel analysis..." -ForegroundColor Cyan
    $jobs = @()
    
    for ($i = 0; $i -lt $activeBatches.Count; $i++) {
        $batch = $activeBatches[$i]
        $batchNumber = $i + 1
        
        Write-Host "Starting Batch $batchNumber with $($batch.Count) tickers: $($batch -join ', ')" -ForegroundColor Magenta
        
        $job = Start-Job -Name "AltmanBatch_$batchNumber" -ScriptBlock {
            param($tickers, $enhancedAnalysis, $quarters)
            
            # Change to the correct directory
            Set-Location $using:PWD
            
            # Build command
            $cmd = @("python", "main.py")
            $cmd += $tickers
            $cmd += "--log-level", "ERROR"
            $cmd += "--progress", "never"
            
            if ($enhancedAnalysis) {
                $cmd += "--enhanced-analysis"
                $cmd += "--quarters", $quarters
            }
            
            # Execute command
            try {
                & $cmd[0] $cmd[1..($cmd.Length - 1)]
                $exitCode = $LASTEXITCODE
            }
            catch {
                $exitCode = -1
            }
            
            return [PSCustomObject]@{
                Tickers  = $tickers
                ExitCode = $exitCode
                Success  = ($exitCode -eq 0)
            }
        } -ArgumentList $batch, $EnhancedAnalysis, $Quarters
        
        $jobs += $job
    }
    
    # Wait for all jobs to complete
    Write-Host "`nWaiting for all batches to complete..." -ForegroundColor Cyan
    
    $completed = 0
    while ($completed -lt $jobs.Count) {
        $runningJobs = $jobs | Where-Object { $_.State -eq "Running" }
        $completedJobs = $jobs | Where-Object { $_.State -eq "Completed" }
        
        if ($completedJobs.Count -gt $completed) {
            $completed = $completedJobs.Count
            Write-Host "Completed: $completed/$($jobs.Count) batches" -ForegroundColor Green
        }
        
        if ($runningJobs.Count -eq 0) {
            break
        }
        
        Start-Sleep -Seconds 2
    }
    
    # Collect results
    $successCount = 0
    $failureCount = 0
    
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job
        if ($result -and $result.Success) {
            $successCount++
        }
        else {
            $failureCount++
        }
        Remove-Job -Job $job
    }
    
    # Final summary
    Write-Host "`nAnalysis complete!" -ForegroundColor Green
    Write-Host "Successful batches: $successCount" -ForegroundColor Green
    Write-Host "Failed batches: $failureCount" -ForegroundColor $(if ($failureCount -eq 0) { "Green" } else { "Red" })
    Write-Host "Total tickers processed: $($tickers.Count)" -ForegroundColor Cyan
    
    if ($failureCount -eq 0) {
        Write-Host "`nAll analysis completed successfully!" -ForegroundColor Green
        Write-Host "Check the 'output' folder for individual ticker results." -ForegroundColor Yellow
    }
    else {
        Write-Host "`nSome batches failed. Check individual ticker outputs and logs." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
