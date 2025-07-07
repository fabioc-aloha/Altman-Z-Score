# ===============================================================================
# Retail Z-Score Visualization Launcher
# ===============================================================================

[CmdletBinding()]
param(
    [string]$DataFile = "",
    [string]$OutputDir = "retail_validation/results",
    [switch]$SaveHTML,
    [switch]$ShowChart,
    [switch]$IncludeStats,
    [switch]$Help
)

function Show-Help {
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host "RETAIL Z-SCORE VISUALIZATION LAUNCHER" -ForegroundColor Yellow
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Creates interactive visualizations of retail Z-Score model performance." -ForegroundColor White
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor White
    Write-Host "  .\visualize_retail_zscore.ps1 [parameters]" -ForegroundColor Gray
    Write-Host ""
    Write-Host "PARAMETERS:" -ForegroundColor White
    Write-Host "  -DataFile STRING    Specific validation results file to visualize" -ForegroundColor Gray
    Write-Host "  -OutputDir STRING   Output directory for charts (default: retail_validation/results)" -ForegroundColor Gray
    Write-Host "  -SaveHTML           Save interactive HTML charts (default: true)" -ForegroundColor Gray
    Write-Host "  -ShowChart          Display chart in browser (default: false)" -ForegroundColor Gray
    Write-Host "  -IncludeStats       Include statistical analysis (default: true)" -ForegroundColor Gray
    Write-Host "  -Help               Show this help message" -ForegroundColor Gray
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor White
    Write-Host "  .\visualize_retail_zscore.ps1" -ForegroundColor Gray
    Write-Host "  .\visualize_retail_zscore.ps1 -ShowChart" -ForegroundColor Gray
    Write-Host "  .\visualize_retail_zscore.ps1 -DataFile 'results/validation_results_20250106.csv'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "FEATURES:" -ForegroundColor White
    Write-Host "  - Interactive scatter plot with threshold zones" -ForegroundColor Green
    Write-Host "  - Color-coded bankruptcy outcomes (green=survived, red=failed)" -ForegroundColor Green
    Write-Host "  - Performance metrics and optimization recommendations" -ForegroundColor Green
    Write-Host "  - Distribution analysis and zone breakdowns" -ForegroundColor Green
    Write-Host ""
}

function Test-Dependencies {
    Write-Host "Checking Python dependencies..." -ForegroundColor Cyan
    
    try {
        # Check if Python is available
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Python is not available. Please install Python 3.7 or higher." -ForegroundColor Red
            return $false
        }
        
        Write-Host "Python version: $pythonVersion" -ForegroundColor Green
        
        # Check required packages
        $requiredPackages = @('pandas', 'numpy', 'plotly', 'pathlib')
        $missingPackages = @()
        
        foreach ($package in $requiredPackages) {
            try {
                python -c "import $package" 2>$null
                if ($LASTEXITCODE -ne 0) {
                    $missingPackages += $package
                }
            }
            catch {
                $missingPackages += $package
            }
        }
        
        if ($missingPackages.Count -gt 0) {
            Write-Host "Missing required packages: $($missingPackages -join ', ')" -ForegroundColor Red
            Write-Host "Installing missing packages..." -ForegroundColor Yellow
            
            foreach ($package in $missingPackages) {
                Write-Host "Installing $package..." -ForegroundColor Yellow
                python -m pip install $package
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "Failed to install $package" -ForegroundColor Red
                    return $false
                }
            }
        }
        
        Write-Host "All dependencies are available." -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error checking dependencies: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-Visualization {
    param(
        [string]$DataFile,
        [string]$OutputDir,
        [bool]$SaveHTML,
        [bool]$ShowChart,
        [bool]$IncludeStats
    )
    
    Write-Host ""
    Write-Host "Starting retail Z-Score visualization..." -ForegroundColor Green
    Write-Host ""
    
    # Build Python command
    $pythonArgs = @()
    $pythonArgs += "retail_validation/scripts/visualize_retail_zscore.py"
    $pythonArgs += "--output-dir"
    $pythonArgs += $OutputDir
    
    if ($DataFile) {
        $pythonArgs += "--data-file"
        $pythonArgs += $DataFile
    }
    
    if ($SaveHTML) {
        $pythonArgs += "--save-html"
    }
    
    if ($ShowChart) {
        $pythonArgs += "--show-chart"
    }
    
    if ($IncludeStats) {
        $pythonArgs += "--include-stats"
    }
    
    Write-Host "CONFIGURATION:" -ForegroundColor Cyan
    Write-Host "  Data File: $(if ($DataFile) { $DataFile } else { 'Most recent validation results' })" -ForegroundColor Gray
    Write-Host "  Output Directory: $OutputDir" -ForegroundColor Gray
    Write-Host "  Save HTML: $SaveHTML" -ForegroundColor Gray
    Write-Host "  Show Chart: $ShowChart" -ForegroundColor Gray
    Write-Host "  Include Stats: $IncludeStats" -ForegroundColor Gray
    Write-Host ""
    
    # Execute Python script
    try {
        Write-Host "Executing: python $($pythonArgs -join ' ')" -ForegroundColor Gray
        Write-Host ""
        
        & python @pythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Visualization completed successfully!" -ForegroundColor Green
            Write-Host "Check the output directory for generated files: $OutputDir" -ForegroundColor Cyan
        }
        else {
            Write-Host ""
            Write-Host "Visualization failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Error executing visualization: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host "RETAIL Z-SCORE VISUALIZATION" -ForegroundColor Yellow
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check dependencies
    if (-not (Test-Dependencies)) {
        Write-Host "Dependency check failed. Please install required packages." -ForegroundColor Red
        return
    }
    
    # Check if we're in the correct directory
    if (-not (Test-Path "retail_validation/scripts/visualize_retail_zscore.py")) {
        Write-Host "Error: Please run this script from the project root directory." -ForegroundColor Red
        Write-Host "Current directory: $(Get-Location)" -ForegroundColor Gray
        return
    }
    
    # Run visualization
    Invoke-Visualization -DataFile $DataFile -OutputDir $OutputDir -SaveHTML $SaveHTML.IsPresent -ShowChart $ShowChart.IsPresent -IncludeStats $IncludeStats.IsPresent
}

# Run the main function
Main
