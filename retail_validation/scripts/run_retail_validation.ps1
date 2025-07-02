# ===============================================================================
# RETAIL Z-SCORE MODEL VALIDATION ORCHESTRATOR
# PowerShell Script for Centralized Retail Model Testing
# ===============================================================================

<#
.SYNOPSIS
    Orchestrates comprehensive validation of the novel retail Z-Score model

.DESCRIPTION
    This script provides a centralized interface for validating the retail Z-Score model 
    using the retail_validation framework. All scripts, configurations, and outputs
    are organized in the retail_validation/ directory for better project organization.

.PARAMETER FullValidation
    Run complete validation including all analyses

.PARAMETER QuickTest
    Run quick validation on subset of companies

.PARAMETER CompareModels
    Compare retail model against traditional models

.PARAMETER SeasonalAnalysis
    Include seasonal pattern analysis

.PARAMETER OutputDir
    Directory for output results (default: retail_validation/results)

.PARAMETER ShowConfig
    Display validation configuration and exit
    
.PARAMETER UseSECEDGAR
    Enable SEC EDGAR retrieval for delisted companies
    
.PARAMETER TestEDGAR
    Test SEC EDGAR retrieval for a specific delisted ticker (e.g. SHLDQ)
    
.PARAMETER ClearCache
    Clear Python cache files (__pycache__ directories and .pyc files) before running

.EXAMPLE
    .\retail_validation\scripts\run_retail_validation.ps1 -FullValidation
    
.EXAMPLE
    .\retail_validation\scripts\run_retail_validation.ps1 -QuickTest

.EXAMPLE
    .\retail_validation\scripts\run_retail_validation.ps1 -ShowConfig
    
.EXAMPLE
    .\retail_validation\scripts\run_retail_validation.ps1 -FullValidation -UseSECEDGAR
    
.EXAMPLE
    .\retail_validation\scripts\run_retail_validation.ps1 -TestEDGAR SHLDQ

.NOTES
    Requires: Python environment with Altman Z-Score project dependencies
    Estimated Runtime: 2-3 hours for full validation, 15-30 minutes for quick test
    Output: Comprehensive validation report and raw results in retail_validation/results/
#>

param(
    [switch]$FullValidation,
    [switch]$QuickTest,
    [switch]$UseSECEDGAR,
    [string]$TestEDGAR,
    [switch]$AvailableOnly,
    [switch]$SampleBankruptcy,
    [switch]$UseHistoricalResults,
    [switch]$CompareModels,
    [switch]$SeasonalAnalysis,
    [string]$OutputDir = "retail_validation/results",
    [switch]$ShowConfig,
    [switch]$ClearCache,
    [switch]$Help
)

# Script configuration
$ScriptName = "Retail Z-Score Model Validation Orchestrator"
$Version = "2.0"
$ValidationRoot = "retail_validation"
$ScriptsDir = "$ValidationRoot/scripts"
$ConfigDir = "$ValidationRoot/config"
$ResultsDir = "$ValidationRoot/results"

function Show-Header {
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "RETAIL Z-SCORE MODEL VALIDATION ORCHESTRATOR" -ForegroundColor Yellow
    Write-Host "Centralized Framework for Novel Retail-Specific Model Testing" -ForegroundColor White
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "Version: $Version" -ForegroundColor Gray
    Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "Validation Framework: $ValidationRoot/" -ForegroundColor Gray
    Write-Host ""
}

function Show-Help {
    Write-Host @"
$ScriptName - Help

DESCRIPTION:
    Centralized orchestrator for the novel retail Z-Score model validation framework.
    All validation scripts, configurations, and outputs are organized in the
    retail_validation/ directory for better project organization and reproducibility.

USAGE:
    .\retail_validation\scripts\run_retail_validation.ps1 [options]

OPTIONS:
    -FullValidation     Complete validation with all analyses (recommended)
    -QuickTest          Quick validation on subset of companies (~11 companies)
    -CompareModels      Include traditional model comparison
    -SeasonalAnalysis   Analyze seasonal inventory patterns
    -OutputDir DIR      Output directory (default: retail_validation/results)
    -ShowConfig         Display validation configuration and exit
    -Help               Show this help message

EXAMPLES:
    # Full comprehensive validation (recommended for academic research)
    .\retail_validation\scripts\run_retail_validation.ps1 -FullValidation

    # Quick validation for development testing
    .\retail_validation\scripts\run_retail_validation.ps1 -QuickTest

    # Show validation configuration
    .\retail_validation\scripts\run_retail_validation.ps1 -ShowConfig

    # Compare retail vs traditional models
    .\retail_validation\scripts\run_retail_validation.ps1 -FullValidation -CompareModels

VALIDATION FRAMEWORK STRUCTURE:
    retail_validation/
    ├── config/
    │   └── validation_config.py      # Centralized configuration
    ├── scripts/
    │   ├── validate_retail_model.py  # Main validation script
    │   └── run_retail_validation.ps1 # This orchestrator script
    └── results/
        └── [timestamped runs]/       # Validation results with timestamps

PORTFOLIO CATEGORIES:
    - Failed/Bankrupt Retailers: Test bankruptcy prediction accuracy
    - Retailers in Distress: Test early warning capability  
    - Recovery/Turnaround Stories: Test model discrimination
    - Stable/Strong Retailers: Test false positive rates
    - Seasonal/Cyclical Retailers: Test seasonal pattern handling

EXPECTED OUTCOMES:
    - Bankruptcy Prediction Accuracy: Target >80% (vs ~65% traditional)
    - Early Warning Lead Time: 2-3 years advance notice
    - False Positive Rate: <15% (vs ~25% traditional)
    - Seasonal Stability: Reduced quarterly variation

OUTPUT FILES:
    - validation_report.md: Comprehensive analysis report
    - raw_results.json: Detailed company-by-company results
    - validation_config_snapshot.json: Configuration used for run
    - [Additional analysis files based on options]

ACADEMIC APPLICATIONS:
    Results support academic publication and peer review of the novel
    retail Z-Score model. Use full validation for research purposes.

"@
}

function Show-ValidationConfig {
    Write-Host "RETAIL VALIDATION CONFIGURATION" -ForegroundColor Yellow
    Write-Host ("=" * 60) -ForegroundColor Gray
    
    try {
        # Get configuration summary from validation config
        $configSummary = python -c "
import sys
sys.path.append('.')
from retail_validation.config.validation_config import get_validation_summary
import json
summary = get_validation_summary()
print(json.dumps(summary, indent=2, default=str))
" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $config = $configSummary | ConvertFrom-Json
            
            Write-Host "Portfolio Information:" -ForegroundColor Cyan
            Write-Host "  Total Companies: $($config.total_companies)" -ForegroundColor White
            Write-Host "  Portfolio File: $($config.portfolio_file)" -ForegroundColor White
            Write-Host "  Results Directory: $($config.results_directory)" -ForegroundColor White
            Write-Host ""
            
            Write-Host "Category Distribution:" -ForegroundColor Cyan
            foreach ($category in $config.categories.PSObject.Properties) {
                Write-Host "  $($category.Name): $($category.Value) companies" -ForegroundColor White
            }
            Write-Host ""
            
            Write-Host "Validation Tests: $($config.validation_tests)" -ForegroundColor Cyan
            Write-Host "Quick Test Companies: $($config.quick_test_companies)" -ForegroundColor Cyan
        }
        else {
            Write-Host "❌ Could not load validation configuration" -ForegroundColor Red
            Write-Host "Error: $configSummary" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error accessing validation configuration: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "[X] Python not found. Please install Python 3.8+" -ForegroundColor Red
        return $false
    }
    
    # Check if we can import required modules
    try {
        # Show Python path to help debug import issues
        Write-Host "Python path:" -ForegroundColor Gray
        python -c "import sys; print('\n'.join(sys.path))" | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        
        # Check basic required modules with more detailed output
        Write-Host "Checking for required modules..." -ForegroundColor Gray
        $baseModuleCheck = python -c "
try:
    import pandas
    print('[OK] pandas ' + pandas.__version__)
    import numpy
    print('[OK] numpy ' + numpy.__version__)
    print('SUCCESS')
except ImportError as e:
    print('ERROR: ' + str(e))
    exit(1)
"
        # Show full module check output for debugging
        $baseModuleCheck | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        
        if ($baseModuleCheck -contains "SUCCESS") {
            Write-Host "[OK] Base Python modules available" -ForegroundColor Green
        }
        else {
            Write-Host "[X] Missing basic Python modules (pandas, numpy). Run: pip install -r requirements.txt" -ForegroundColor Red
            return $false
        }
        
        # Check SEC EDGAR required modules if testing that functionality
        if ($UseSECEDGAR -or $TestEDGAR) {
            $secModuleCheck = python -c "
try:
    import bs4
    print('[OK] beautifulsoup4 ' + bs4.__version__)
    import aiohttp
    print('[OK] aiohttp ' + aiohttp.__version__)
    print('SUCCESS')
except ImportError as e:
    print('ERROR: ' + str(e))
    exit(1)
"
            # Show full module check output for debugging
            $secModuleCheck | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
            
            if ($secModuleCheck -contains "SUCCESS") {
                Write-Host "[OK] SEC EDGAR modules available" -ForegroundColor Green
            }
            else {
                Write-Host "[X] Missing SEC EDGAR modules (beautifulsoup4, aiohttp). Run: pip install -r requirements.txt" -ForegroundColor Red
                return $false
            }
        }
    }
    catch {
        Write-Host "❌ Error checking Python modules: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Gray
        return $false
    }
    
    # Check project structure
    if (-not (Test-Path "altman_zscore")) {
        Write-Host "❌ altman_zscore module not found. Run from project root." -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Project structure verified" -ForegroundColor Green
    
    # Check validation framework structure
    if (-not (Test-Path $ValidationRoot)) {
        Write-Host "❌ Validation framework not found: $ValidationRoot/" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Validation framework found" -ForegroundColor Green
    
    # Check portfolio file
    if (-not (Test-Path "portfolios/retail_backtest_portfolio.txt")) {
        Write-Host "❌ Retail backtest portfolio file not found" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Retail backtest portfolio found" -ForegroundColor Green
    
    # Check validation script
    if (-not (Test-Path "$ScriptsDir/validate_retail_model.py")) {
        Write-Host "❌ Validation script not found: $ScriptsDir/validate_retail_model.py" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Validation script available" -ForegroundColor Green
    
    # Check configuration
    if (-not (Test-Path "$ConfigDir/validation_config.py")) {
        Write-Host "❌ Validation configuration not found: $ConfigDir/validation_config.py" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Validation configuration available" -ForegroundColor Green
    
    # Check if retail model is implemented
    try {
        $retailModelCheck = python -c "from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculator; calc = ZScoreCalculator(); print('[OK] Retail model implementation found' if hasattr(calc, '_calculate_retail_zscore') else '[X] Retail model not implemented')" 2>&1
        if ($retailModelCheck -match "\[OK\]") {
            Write-Host "[OK] Retail model implementation verified" -ForegroundColor Green
        }
        else {
            Write-Host "[X] Retail model implementation not found" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "⚠️ Could not verify retail model implementation" -ForegroundColor Yellow
    }
    
    Write-Host ""
    return $true
}

function Show-PortfolioSummary {
    Write-Host "RETAIL VALIDATION PORTFOLIO SUMMARY" -ForegroundColor Yellow
    Write-Host ("-" * 50) -ForegroundColor Gray
    
    try {
        # Get portfolio summary from validation config
        python -c "
import sys
sys.path.append('.')
from retail_validation.config.validation_config import get_validation_summary
summary = get_validation_summary()
print(f'Total Companies: {summary[\"total_companies\"]}')
print(f'Portfolio File: {summary[\"portfolio_file\"]}')
print('')
print('Category Distribution:')
for category, count in summary['categories'].items():
    print(f'  • {category.capitalize()}: {count} companies')
print('')
print('Validation Framework:')
print(f'  • Validation Tests: {summary[\"validation_tests\"]}')
print(f'  • Quick Test Companies: {summary[\"quick_test_companies\"]}')
"
    }
    catch {
        Write-Host "❌ Could not load portfolio summary" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "VALIDATION OBJECTIVES:" -ForegroundColor Yellow
    Write-Host "  • Test bankruptcy prediction accuracy vs traditional models" -ForegroundColor White
    Write-Host "  • Validate inventory turnover component (X₆) effectiveness" -ForegroundColor White
    Write-Host "  • Assess modified working capital calculation (X₁)" -ForegroundColor White
    Write-Host "  • Analyze seasonal pattern handling capabilities" -ForegroundColor White
    Write-Host "  • Generate academic-quality validation report" -ForegroundColor White
    Write-Host ""
}

function Start-FullValidation {
    Write-Host "STARTING FULL VALIDATION" -ForegroundColor Yellow
    Write-Host "This comprehensive analysis will take 2-3 hours..." -ForegroundColor Gray
    Write-Host ""
    
    $pythonArgs = @(
        "$ScriptsDir/validate_retail_model.py",
        "--output-dir", $OutputDir,
        "--comparison",
        "--detailed"
    )
    
    if ($SeasonalAnalysis) {
        $pythonArgs += "--seasonal"
    }
    
    if ($UseSECEDGAR) {
        $pythonArgs += "--use-sec-edgar"
    }
    
    Write-Host "Running: python $($pythonArgs -join ' ')" -ForegroundColor Gray
    python @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Full validation completed successfully" -ForegroundColor Green
        Show-Results
    }
    else {
        Write-Host "❌ Validation failed with exit code $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Check the Python output above for specific error details" -ForegroundColor Yellow
    }
}

function Start-QuickTest {
    Write-Host "STARTING QUICK VALIDATION TEST" -ForegroundColor Yellow
    Write-Host "Testing subset of companies for development..." -ForegroundColor Gray
    Write-Host ""
    
    $pythonArgs = @(
        "$ScriptsDir/validate_retail_model.py",
        "--output-dir", $OutputDir,
        "--quick-test"
    )
    
    if ($CompareModels) {
        $pythonArgs += "--comparison"
    }
    
    if ($SeasonalAnalysis) {
        $pythonArgs += "--seasonal"
    }
    
    if ($UseSECEDGAR) {
        $pythonArgs += "--use-sec-edgar"
    }
    
    Write-Host "Running: python $($pythonArgs -join ' ')" -ForegroundColor Gray
    python @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Quick test completed successfully" -ForegroundColor Green
        Show-Results
    }
    else {
        Write-Host "❌ Quick test failed with exit code $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Check the Python output above for specific error details" -ForegroundColor Yellow
    }
}

function Start-ModelComparison {
    Write-Host "RUNNING MODEL COMPARISON ANALYSIS" -ForegroundColor Yellow
    Write-Host "Comparing retail model vs traditional Z-Score models..." -ForegroundColor Gray
    Write-Host ""
    
    # Create comparison results directory
    $comparisonDir = "$OutputDir/comparison"
    if (-not (Test-Path $comparisonDir)) {
        New-Item -ItemType Directory -Path $comparisonDir -Force | Out-Null
    }
    
    # Run retail model analysis
    Write-Host "1. Analyzing with retail model..." -ForegroundColor Cyan
    python main.py --portfolio-file portfolios/retail_backtest_portfolio.txt --model retail
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Retail model analysis failed with exit code $LASTEXITCODE" -ForegroundColor Red
        return
    }
    
    # Run traditional model analysis  
    Write-Host "2. Analyzing with original model..." -ForegroundColor Cyan
    python main.py --portfolio-file portfolios/retail_backtest_portfolio.txt --model original
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Traditional model analysis failed with exit code $LASTEXITCODE" -ForegroundColor Red
        return
    }
    
    # Run comparison validation
    Write-Host "3. Generating comparative analysis..." -ForegroundColor Cyan
    python "$ScriptsDir/validate_retail_model.py" --output-dir $comparisonDir --comparison --detailed
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model comparison completed successfully" -ForegroundColor Green
        Show-Results $comparisonDir
    }
    else {
        Write-Host "❌ Model comparison failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
}

function Show-Results {
    param([string]$ResultsDir = $OutputDir)
    
    Write-Host ""
    Write-Host "VALIDATION RESULTS" -ForegroundColor Yellow
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    # Find the most recent validation run
    $latestRun = Get-ChildItem $ResultsDir -Directory | 
    Where-Object { $_.Name -match "^\w+_\d{8}_\d{6}$" } |
    Sort-Object Name -Descending |
    Select-Object -First 1
    
    if ($latestRun) {
        $runPath = $latestRun.FullName
        Write-Host "Latest Validation Run: $($latestRun.Name)" -ForegroundColor Cyan
        
        if (Test-Path "$runPath/validation_report.md") {
            Write-Host "📊 Validation Report: $runPath/validation_report.md" -ForegroundColor Green
            
            # Show key metrics from report if available
            try {
                $report = Get-Content "$runPath/validation_report.md" -Raw
                if ($report -match "Retail Model Accuracy: (\d+\.?\d*)%") {
                    Write-Host "   Bankruptcy Prediction Accuracy: $($matches[1])%" -ForegroundColor White
                }
                if ($report -match "Improvement: ([+-]\d+\.?\d*)%") {
                    $improvement = $matches[1]
                    $color = if ($improvement -like "+*") { "Green" } else { "Red" }
                    Write-Host "   Improvement over Traditional: $improvement%" -ForegroundColor $color
                }
                if ($report -match "Target Met: (✅ YES|❌ NO)") {
                    $targetMet = $matches[1]
                    $color = if ($targetMet -like "*YES*") { "Green" } else { "Red" }
                    Write-Host "   Validation Targets: $targetMet" -ForegroundColor $color
                }
            }
            catch {
                # Silent fail if report parsing fails
            }
        }
        
        if (Test-Path "$runPath/raw_results.json") {
            Write-Host "📈 Raw Results: $runPath/raw_results.json" -ForegroundColor Green
        }
        
        if (Test-Path "$runPath/validation_config_snapshot.json") {
            Write-Host "⚙️ Configuration: $runPath/validation_config_snapshot.json" -ForegroundColor Green
        }
    }
    else {
        Write-Host "No validation runs found in $ResultsDir" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "  1. Review validation report for detailed analysis" -ForegroundColor White
    Write-Host "  2. Check bankruptcy prediction accuracy vs targets" -ForegroundColor White
    Write-Host "  3. Analyze inventory component effectiveness" -ForegroundColor White
    Write-Host "  4. Consider model refinements based on results" -ForegroundColor White
    Write-Host "  5. Use results for academic publication preparation" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Results directory: $ResultsDir" -ForegroundColor Cyan
}

function Test-SECEDGARRetrieval {
    param(
        [string]$Ticker
    )
    
    Write-Host "SEC EDGAR DATA RETRIEVAL TEST" -ForegroundColor Yellow
    Write-Host "=============================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Testing SEC EDGAR integration with ticker: $Ticker" -ForegroundColor Cyan
    Write-Host ""
    
    $pythonArgs = @(
        "$ScriptsDir/validate_retail_model.ps1",
        "--test-edgar", $Ticker,
        "--use-sec-edgar"
    )
    
    Write-Host "Running: python $($pythonArgs -join ' ')" -ForegroundColor Gray
    python @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SEC EDGAR test completed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "❌ SEC EDGAR test failed" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "For more detailed SEC EDGAR testing, try:" -ForegroundColor Cyan
    Write-Host "  .\retail_validation\scripts\get_sec_edgar_data.ps1 -Ticker $Ticker" -ForegroundColor Gray
}

function Clear-PythonCache {
    Write-Host "Clearing Python cache files..." -ForegroundColor Yellow
    
    # Find and remove all __pycache__ directories
    $pycacheCount = 0
    $pyccacheSize = 0
    
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
        $dirSize = (Get-ChildItem $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $pyccacheSize += $dirSize
        $pycacheCount++
        
        Write-Host "  Removing: $($_.FullName)" -ForegroundColor Gray
        Remove-Item -Path $_.FullName -Recurse -Force
    }
    
    # Find and remove .pyc files
    $pycFiles = @(Get-ChildItem -Path . -Recurse -File -Filter "*.pyc")
    $pycFilesSize = ($pycFiles | Measure-Object -Property Length -Sum).Sum
    $pyccacheSize += $pycFilesSize
    
    foreach ($file in $pycFiles) {
        Write-Host "  Removing: $($file.FullName)" -ForegroundColor Gray
        Remove-Item -Path $file.FullName -Force
    }
    
    # Calculate total size in KB
    $totalSizeKB = [math]::Round($pyccacheSize / 1KB, 2)
    
    Write-Host "[OK] Removed $pycacheCount __pycache__ directories and $($pycFiles.Count) .pyc files" -ForegroundColor Green
    Write-Host "[OK] Freed up approximately $totalSizeKB KB of disk space" -ForegroundColor Green
    Write-Host ""
}

function Main {
    Show-Header
    
    if ($Help) {
        Show-Help
        return
    }
    
    if ($ClearCache) {
        Clear-PythonCache
    }
    
    if ($ShowConfig) {
        Show-ValidationConfig
        return
    }
    
    if (-not (Test-Prerequisites)) {
        Write-Host "Prerequisites check failed. Exiting." -ForegroundColor Red
        return
    }
    
    Show-PortfolioSummary
    
    # Create output directory
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        Write-Host "Created output directory: $OutputDir" -ForegroundColor Green
    }
    
    # Execute based on parameters
    # If only ClearCache was specified and no other action, show message and exit
    if ($ClearCache -and -not ($TestEDGAR -or $FullValidation -or $QuickTest -or $CompareModels)) {
        Write-Host "[OK] Python cache files cleared. No validation action specified." -ForegroundColor Green
        Write-Host "Use -TestEDGAR, -FullValidation, or -QuickTest to run validation." -ForegroundColor Yellow
        return
    }
    
    if ($TestEDGAR) {
        Test-SECEDGARRetrieval -Ticker $TestEDGAR
    }
    elseif ($FullValidation) {
        Start-FullValidation
    }
    elseif ($QuickTest) {
        Start-QuickTest
    }
    elseif ($CompareModels) {
        Start-ModelComparison
    }
    elseif ($ClearCache) {
        Clear-PythonCache
    }
    else {
        Write-Host "No validation type specified. Use -Help for options." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Quick start options:" -ForegroundColor White
        Write-Host "  .\retail_validation\scripts\run_retail_validation.ps1 -FullValidation    # Complete analysis" -ForegroundColor Gray
        Write-Host "  .\retail_validation\scripts\run_retail_validation.ps1 -QuickTest        # Development test" -ForegroundColor Gray
        Write-Host "  .\retail_validation\scripts\run_retail_validation.ps1 -ShowConfig       # Show configuration" -ForegroundColor Gray
        Write-Host "  .\retail_validation\scripts\run_retail_validation.ps1 -TestEDGAR SHLDQ  # Test SEC EDGAR" -ForegroundColor Gray
        Write-Host "  .\retail_validation\scripts\run_retail_validation.ps1 -ClearCache       # Clear Python cache" -ForegroundColor Gray
        Write-Host "  .\retail_validation\scripts\run_retail_validation.ps1 -Help             # Show all options" -ForegroundColor Gray
    }
}

# Execute main function
Main
