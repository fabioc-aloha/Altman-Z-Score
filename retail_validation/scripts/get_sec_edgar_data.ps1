# ===============================================================================
# SEC EDGAR DATA RETRIEVAL
# PowerShell Script for Testing SEC EDGAR Integration
# ===============================================================================

<#
.SYNOPSIS
    Retrieves financial data for a delisted company from SEC EDGAR

.DESCRIPTION
    This script demonstrates the SEC EDGAR integration by retrieving 
    historical financial data for a specified delisted company ticker.

.PARAMETER Ticker
    The ticker symbol of the delisted company to retrieve data for

.EXAMPLE
    .\retail_validation\scripts\get_sec_edgar_data.ps1 -Ticker SHLDQ
    
.NOTES
    Requires: Python environment with Altman Z-Score project dependencies
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Ticker
)

# Find the project root directory
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Set working directory to project root
Push-Location $ProjectRoot

Write-Host "SEC EDGAR Data Retrieval" -ForegroundColor Yellow
Write-Host "======================" -ForegroundColor Yellow
Write-Host ""
# Run the Python script
Write-Host "Retrieving data for ticker: $Ticker" -ForegroundColor Cyan
python retail_validation/scripts/get_sec_edgar_data.py $Ticker

# Return to original directory
Pop-Location
