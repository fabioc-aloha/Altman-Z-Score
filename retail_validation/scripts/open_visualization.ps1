# ===============================================================================
# Open Latest Retail Z-Score Visualization
# ===============================================================================

param(
    [string]$Type = "dashboard"  # Options: scatter, distribution, dashboard
)

function Find-LatestVisualization {
    param([string]$Type)
    
    $resultsDir = "retail_validation\results"
    $pattern = "*retail_zscore_${Type}_*.html"
    
    $files = Get-ChildItem $resultsDir -Filter $pattern | Sort-Object LastWriteTime -Descending
    
    if ($files.Count -eq 0) {
        Write-Host "No visualization files found for type: $Type" -ForegroundColor Red
        Write-Host "Available types: scatter, distribution, dashboard" -ForegroundColor Gray
        return $null
    }
    
    return $files[0].FullName
}

function Open-Visualization {
    param([string]$FilePath)
    
    if (-not $FilePath) {
        return
    }
    
    Write-Host "Opening visualization: $FilePath" -ForegroundColor Green
    
    try {
        Start-Process $FilePath
    }
    catch {
        Write-Host "Error opening file: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Try opening manually: $FilePath" -ForegroundColor Yellow
    }
}

# Main execution
Write-Host ""
Write-Host "RETAIL Z-SCORE VISUALIZATION OPENER" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$latestFile = Find-LatestVisualization -Type $Type

if ($latestFile) {
    Open-Visualization -FilePath $latestFile
}
else {
    Write-Host "Run the visualization script first:" -ForegroundColor Yellow
    Write-Host "  .\retail_validation\scripts\visualize_retail_zscore.ps1 -SaveHTML -IncludeStats" -ForegroundColor Gray
}
