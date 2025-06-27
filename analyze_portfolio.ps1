<#
.SYNOPSIS
    Quick portfolio analysis with sensible defaults

.DESCRIPTION
    Simple wrapper for parallel portfolio analysis with preset configurations
    for different account types and use cases.

.PARAMETER Portfolio
    Portfolio name or file path (supports: my, tech, international, diversified, or custom file path)

.PARAMETER Mode
    Analysis mode: fast (2 processes), balanced (4 processes), intensive (6 processes)

.PARAMETER AccountType
    FMP account type: free or enhanced (affects default settings)

.PARAMETER Help
    Display help information and usage examples

.EXAMPLE
    .\analyze_portfolio.ps1 -Help

.EXAMPLE
    .\analyze_portfolio.ps1 -Portfolio my -Mode balanced

.EXAMPLE
    .\analyze_portfolio.ps1 -Portfolio international -Mode intensive -AccountType enhanced

.EXAMPLE
    .\analyze_portfolio.ps1 -Portfolio tech -Mode fast
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$Portfolio,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("fast", "balanced", "intensive")]
    [string]$Mode = "balanced",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("free", "enhanced")]
    [string]$AccountType = "free",
    
    [Parameter(Mandatory = $false)]
    [switch]$Help
)

function Show-Help {
    <#
    .SYNOPSIS
        Display help information for the quick portfolio analysis script
    #>
    
    Write-Host "`nQuick Portfolio Analysis with Sensible Defaults" -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Cyan
    
    Write-Host "`nDESCRIPTION:" -ForegroundColor Yellow
    Write-Host "  Simple wrapper for parallel portfolio analysis with preset configurations"
    Write-Host "  for different account types and use cases. Provides sensible defaults"
    Write-Host "  and predefined portfolio mappings for quick analysis."
    
    Write-Host "`nUSAGE:" -ForegroundColor Yellow
    Write-Host "  .\analyze_portfolio.ps1 -Portfolio <name|file> [options]"
    
    Write-Host "`nREQUIRED PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -Portfolio <String>"
    Write-Host "      Portfolio name or custom file path"
    Write-Host "      Built-in portfolios: my, tech, international, diversified"
    Write-Host "      Or provide path to custom portfolio file"
    
    Write-Host "`nOPTIONAL PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -Mode <String>"
    Write-Host "      Analysis mode (default: balanced)"
    Write-Host "      • fast      - 2 parallel processes, quick analysis"
    Write-Host "      • balanced  - 4 parallel processes, standard analysis"
    Write-Host "      • intensive - 6 parallel processes, thorough analysis"
    
    Write-Host "  -AccountType <String>"
    Write-Host "      FMP account type (default: free)"
    Write-Host "      • free     - Basic analysis, 4 quarters"
    Write-Host "      • enhanced - Advanced analysis, 12 quarters, enhanced indicators"
    
    Write-Host "  -Help"
    Write-Host "      Display this help information"
    
    Write-Host "`nPREDEFINED PORTFOLIOS:" -ForegroundColor Yellow
    Write-Host "  • my           - portfolios/my_portfolio.txt"
    Write-Host "  • tech         - portfolios/tech_portfolio.txt"
    Write-Host "  • international- portfolios/international_portfolio.txt"
    Write-Host "  • diversified  - portfolios/diversified_portfolio.txt"
    
    Write-Host "`nMODE CONFIGURATIONS:" -ForegroundColor Yellow
    Write-Host "  • fast      - 2 processes, good for small portfolios or testing"
    Write-Host "  • balanced  - 4 processes, recommended for most portfolios"
    Write-Host "  • intensive - 6 processes, best for large portfolios with powerful systems"
    
    Write-Host "`nEXAMPLES:" -ForegroundColor Yellow
    Write-Host "  # Quick analysis of tech portfolio"
    Write-Host "  .\analyze_portfolio.ps1 -Portfolio tech"
    
    Write-Host "`n  # Fast analysis for testing"
    Write-Host "  .\analyze_portfolio.ps1 -Portfolio my -Mode fast"
    
    Write-Host "`n  # Enhanced analysis with advanced features"
    Write-Host "  .\analyze_portfolio.ps1 -Portfolio international -AccountType enhanced"
    
    Write-Host "`n  # Intensive analysis for large portfolio"
    Write-Host "  .\analyze_portfolio.ps1 -Portfolio diversified -Mode intensive -AccountType enhanced"
    
    Write-Host "`n  # Custom portfolio file"
    Write-Host "  .\analyze_portfolio.ps1 -Portfolio 'custom/my_stocks.txt' -Mode balanced"
    
    Write-Host "`nOUTPUT:" -ForegroundColor Yellow
    Write-Host "  Results are saved to the 'output' folder with individual ticker subdirectories"
    Write-Host "  Each ticker gets: charts, reports, CSV data, and AI insights"
    
    Write-Host "`nACCOUNT TYPE DIFFERENCES:" -ForegroundColor Yellow
    Write-Host "  FREE ACCOUNT:"
    Write-Host "  • 4 quarters of historical data"
    Write-Host "  • Basic financial indicators"
    Write-Host "  • Standard Z-Score analysis"
    
    Write-Host "`n  ENHANCED ACCOUNT:"
    Write-Host "  • 12 quarters of historical data"
    Write-Host "  • Advanced financial indicators"
    Write-Host "  • Enhanced AI insights"
    Write-Host "  • Comprehensive investment reports"
    
    Write-Host "`nTIPS:" -ForegroundColor Yellow
    Write-Host "  • Start with 'balanced' mode for most use cases"
    Write-Host "  • Use 'fast' mode for testing or small portfolios"
    Write-Host "  • Use 'intensive' mode only on powerful systems"
    Write-Host "  • Enhanced account provides significantly more insights"
    
    Write-Host "`nFor more information, see the project documentation or run:"
    Write-Host "  Get-Help .\analyze_portfolio.ps1 -Full"
    Write-Host ""
}

# Check if help was requested or no parameters provided
if ($Help -or (-not $Portfolio)) {
    Show-Help
    exit 0
}

# Resolve portfolio file path
$portfolioMappings = @{
    "my"            = "portfolios/my_portfolio.txt"
    "tech"          = "portfolios/tech_portfolio.txt"
    "international" = "portfolios/international_portfolio.txt"
    "diversified"   = "portfolios/diversified_portfolio.txt"
}

if ($portfolioMappings.ContainsKey($Portfolio.ToLower())) {
    $portfolioFile = $portfolioMappings[$Portfolio.ToLower()]
    $portfolioName = $Portfolio.ToUpper()
}
elseif (Test-Path $Portfolio) {
    $portfolioFile = $Portfolio
    $portfolioName = (Split-Path $Portfolio -Leaf) -replace '\.(txt|csv)$', ''
}
else {
    Write-Host "Portfolio not found: $Portfolio" -ForegroundColor Red
    Write-Host "Available portfolios: my, tech, international, diversified" -ForegroundColor Yellow
    Write-Host "Or provide a valid file path" -ForegroundColor Yellow
    exit 1
}

# Configuration based on mode
$processConfig = @{
    "fast"      = 2
    "balanced"  = 4
    "intensive" = 6
}

$parallelProcesses = $processConfig[$Mode]

# Configuration based on account type
$enhancedAnalysis = ($AccountType -eq "enhanced")
if ($AccountType -eq "enhanced") {
    $quarters = 12
}
else {
    $quarters = 4
}

# Display configuration
Write-Host "`n$portfolioName Portfolio Analysis" -ForegroundColor Cyan
Write-Host "Mode: $Mode ($parallelProcesses processes)" -ForegroundColor Yellow
Write-Host "Account Type: $AccountType" -ForegroundColor Yellow
if ($enhancedAnalysis) {
    Write-Host "Enhanced Analysis: Enabled (${quarters} quarters)" -ForegroundColor Green
}
else {
    Write-Host "Enhanced Analysis: Disabled (${quarters} quarters)" -ForegroundColor Gray
}
Write-Host "Portfolio File: $portfolioFile" -ForegroundColor Gray

# Build arguments for the main script
$scriptArgs = @{
    PortfolioFile     = $portfolioFile
    ParallelProcesses = $parallelProcesses
    Quarters          = $quarters
}

if ($enhancedAnalysis) {
    $scriptArgs.EnhancedAnalysis = $true
}

# Execute the main parallel processing script
try {
    & ".\run_parallel_portfolio.ps1" @scriptArgs
}
catch {
    Write-Host "Failed to execute parallel analysis: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
