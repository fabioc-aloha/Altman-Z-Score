# ===============================================================================
# RETAIL Z-SCORE MODEL VALIDATION SCRIPT
# PowerShell Script for Comprehensive Retail Model Testing
# ===============================================================================

<#
.SYNOPSIS
    Validates the novel retail Z-Score model using the retail backtest portfolio

.DESCRIPTION
    This script runs comprehensive validation of the retail Z-Score model against
    a curated dataset of retail companies including bankrupt, distressed, stable,
    and seasonal retailers. It compares the retail model performance against
    traditional Z-Score models.

.PARAMETER FullValidation
    Run complete validation including all analyses

.PARAMETER QuickTest
    Run quick validation on a subset of companies

.PARAMETER CompareModels
    Compare retail model against traditional models

.PARAMETER SeasonalAnalysis
    Include seasonal pattern analysis

.PARAMETER OutputDir
    Directory for output results (default: backtest_results)

.EXAMPLE
    .\run_retail_validation.ps1 -FullValidation
    
.EXAMPLE
    .\run_retail_validation.ps1 -QuickTest -CompareModels

.NOTES
    Requires: Python environment with Altman Z-Score project dependencies
    Estimated Runtime: 2-3 hours for full validation
    Output: Comprehensive validation report and raw results
#>

param(
    [switch]$FullValidation,
    [switch]$QuickTest,
    [switch]$CompareModels,
    [switch]$SeasonalAnalysis,
    [string]$OutputDir = "backtest_results",
    [switch]$Help
)

# Script configuration
$ScriptName = "Retail Z-Score Model Validation"
$Version = "1.0"

function Show-Header {
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "RETAIL Z-SCORE MODEL VALIDATION" -ForegroundColor Yellow
    Write-Host "Novel Retail-Specific Bankruptcy Prediction Model Testing" -ForegroundColor White
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "Version: $Version" -ForegroundColor Gray
    Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
}

function Show-Help {
    Write-Host @"
$ScriptName - Help

DESCRIPTION:
    Validates the novel retail Z-Score model documented in NOVEL_RETAIL_MODEL.md
    against a comprehensive portfolio of retail companies across different
    financial health scenarios.

USAGE:
    .\run_retail_validation.ps1 [options]

OPTIONS:
    -FullValidation     Complete validation with all analyses (recommended)
    -QuickTest          Quick validation on subset of companies
    -CompareModels      Include traditional model comparison
    -SeasonalAnalysis   Analyze seasonal inventory patterns
    -OutputDir DIR      Output directory (default: backtest_results)
    -Help               Show this help message

EXAMPLES:
    # Full comprehensive validation (recommended for academic research)
    .\run_retail_validation.ps1 -FullValidation

    # Quick validation for development testing
    .\run_retail_validation.ps1 -QuickTest

    # Compare retail vs traditional models
    .\run_retail_validation.ps1 -CompareModels

    # Include seasonal pattern analysis
    .\run_retail_validation.ps1 -SeasonalAnalysis

PORTFOLIO CATEGORIES:
    - Failed/Bankrupt Retailers (20 companies): Test bankruptcy prediction
    - Retailers in Distress (15 companies): Test early warning capability
    - Recovery/Turnaround Stories (10 companies): Test model discrimination
    - Stable/Strong Retailers (15 companies): Test false positive rates
    - Seasonal/Cyclical Retailers (15 companies): Test seasonal handling

EXPECTED OUTCOMES:
    - Bankruptcy Prediction Accuracy: Target >80% (vs ~65% traditional)
    - Early Warning Lead Time: 2-3 years advance notice
    - False Positive Rate: <15% (vs ~25% traditional)
    - Seasonal Stability: Reduced quarterly variation

OUTPUT FILES:
    - validation_report.md: Comprehensive analysis report
    - raw_results.json: Detailed company-by-company results
    - comparative_analysis.xlsx: Model comparison data
    - bankruptcy_prediction_analysis.csv: Bankruptcy prediction details

ACADEMIC APPLICATIONS:
    Results support academic publication and peer review of the novel
    retail Z-Score model. Use full validation for research purposes.

"@
}

function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
        return $false
    }
    
    # Check project structure
    if (-not (Test-Path "altman_zscore")) {
        Write-Host "❌ altman_zscore module not found. Run from project root." -ForegroundColor Red
        return $false
    }
    Write-Host "✅ Project structure verified" -ForegroundColor Green
    
    # Check portfolio file
    if (-not (Test-Path "portfolios/retail_backtest_portfolio.txt")) {
        Write-Host "❌ Retail backtest portfolio file not found" -ForegroundColor Red
        return $false
    }
    Write-Host "✅ Retail backtest portfolio found" -ForegroundColor Green
    
    # Check validation script
    if (-not (Test-Path "validate_retail_model.py")) {
        Write-Host "❌ Validation script not found" -ForegroundColor Red
        return $false
    }
    Write-Host "✅ Validation script available" -ForegroundColor Green
    
    Write-Host ""
    return $true
}

function Show-PortfolioSummary {
    Write-Host "RETAIL BACKTEST PORTFOLIO SUMMARY" -ForegroundColor Yellow
    Write-Host ("-" * 50) -ForegroundColor Gray
    
    $categories = @{
        "Failed/Bankrupt Retailers"   = 20
        "Retailers in Distress"       = 15
        "Recovery/Turnaround Stories" = 10
        "Stable/Strong Retailers"     = 15
        "Seasonal/Cyclical Retailers" = 15
    }
    
    $total = 0
    foreach ($category in $categories.GetEnumerator()) {
        Write-Host "  $($category.Key): $($category.Value) companies" -ForegroundColor White
        $total += $category.Value
    }
    
    Write-Host ("-" * 50) -ForegroundColor Gray
    Write-Host "  TOTAL: $total companies" -ForegroundColor Cyan
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
        "validate_retail_model.py",
        "--portfolio", "portfolios/retail_backtest_portfolio.txt",
        "--output-dir", $OutputDir,
        "--comparison",
        "--detailed"
    )
    
    if ($SeasonalAnalysis) {
        $pythonArgs += "--seasonal"
    }
    
    Write-Host "Running: python $($pythonArgs -join ' ')" -ForegroundColor Gray
    python @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Full validation completed successfully" -ForegroundColor Green
        Show-Results
    }
    else {
        Write-Host "❌ Validation failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
}

function Start-QuickTest {
    Write-Host "STARTING QUICK VALIDATION TEST" -ForegroundColor Yellow
    Write-Host "Testing subset of companies for development..." -ForegroundColor Gray
    Write-Host ""
    
    # Create quick test portfolio with representative companies
    $quickPortfolio = @"
# Quick Test Portfolio for Retail Model Validation
# Representative companies from each category

# Failed Retailers
TOY
SHLDQ
JCPNQ

# Distressed Retailers  
BBBY
GME
M

# Stable Retailers
AMZN
COST
HD

# Seasonal Retailers
SPIR
TSCO
"@
    
    $quickFile = "portfolios/retail_quick_test.txt"
    $quickPortfolio | Out-File -FilePath $quickFile -Encoding UTF8
    
    $pythonArgs = @(
        "validate_retail_model.py",
        "--portfolio", $quickFile,
        "--output-dir", "$OutputDir/quick_test"
    )
    
    if ($CompareModels) {
        $pythonArgs += "--comparison"
    }
    
    Write-Host "Running: python $($pythonArgs -join ' ')" -ForegroundColor Gray
    python @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Quick test completed successfully" -ForegroundColor Green
        Show-Results "$OutputDir/quick_test"
    }
    else {
        Write-Host "❌ Quick test failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
}

function Start-ModelComparison {
    Write-Host "RUNNING MODEL COMPARISON ANALYSIS" -ForegroundColor Yellow
    Write-Host "Comparing retail model vs traditional Z-Score models..." -ForegroundColor Gray
    Write-Host ""
    
    # Run retail model analysis
    Write-Host "1. Analyzing with retail model..." -ForegroundColor Cyan
    python main.py --portfolio portfolios/retail_backtest_portfolio.txt --model retail --output "$OutputDir/retail_results"
    
    # Run traditional model analysis
    Write-Host "2. Analyzing with original model..." -ForegroundColor Cyan
    python main.py --portfolio portfolios/retail_backtest_portfolio.txt --model original --output "$OutputDir/original_results"
    
    # Run comparison validation
    Write-Host "3. Generating comparative analysis..." -ForegroundColor Cyan
    python validate_retail_model.py --portfolio portfolios/retail_backtest_portfolio.txt --output-dir $OutputDir --comparison
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model comparison completed successfully" -ForegroundColor Green
        Show-Results
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
    
    if (Test-Path "$ResultsDir/validation_report.md") {
        Write-Host "📊 Validation Report: $ResultsDir/validation_report.md" -ForegroundColor Green
        
        # Show key metrics from report if available
        try {
            $report = Get-Content "$ResultsDir/validation_report.md" -Raw
            if ($report -match "Retail Model Accuracy: (\d+\.?\d*)%") {
                Write-Host "   Bankruptcy Prediction Accuracy: $($matches[1])%" -ForegroundColor White
            }
            if ($report -match "Improvement: ([+-]\d+\.?\d*)%") {
                $improvement = $matches[1]
                $color = if ($improvement -like "+*") { "Green" } else { "Red" }
                Write-Host "   Improvement over Traditional: $improvement%" -ForegroundColor $color
            }
        }
        catch {
            # Silent fail if report parsing fails
        }
    }
    
    if (Test-Path "$ResultsDir/raw_results.json") {
        Write-Host "📈 Raw Results: $ResultsDir/raw_results.json" -ForegroundColor Green
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

function Main {
    Show-Header
    
    if ($Help) {
        Show-Help
        return
    }
    
    if (-not (Test-Prerequisites)) {
        Write-Host "Prerequisites check failed. Exiting." -ForegroundColor Red
        return
    }
    
    Show-PortfolioSummary
    
    # Create output directory
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
        Write-Host "Created output directory: $OutputDir" -ForegroundColor Green
    }
    
    # Execute based on parameters
    if ($FullValidation) {
        Start-FullValidation
    }
    elseif ($QuickTest) {
        Start-QuickTest
    }
    elseif ($CompareModels) {
        Start-ModelComparison
    }
    else {
        Write-Host "No validation type specified. Use -Help for options." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Quick start options:" -ForegroundColor White
        Write-Host "  .\run_retail_validation.ps1 -FullValidation    # Complete analysis" -ForegroundColor Gray
        Write-Host "  .\run_retail_validation.ps1 -QuickTest        # Development test" -ForegroundColor Gray
        Write-Host "  .\run_retail_validation.ps1 -Help             # Show all options" -ForegroundColor Gray
    }
}

# Execute main function
Main
