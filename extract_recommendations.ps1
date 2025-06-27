$outputDir = "c:\Development\Altman-Z-Score-1\output"
$results = @{}

# Get all company folders
$companyFolders = Get-ChildItem -Path $outputDir -Directory

foreach ($companyFolder in $companyFolders) {
    $ticker = $companyFolder.Name
    $reportPath = Join-Path $companyFolder.FullName "${ticker}_comprehensive_report.html"
    
    if (Test-Path $reportPath) {
        $content = Get-Content -Path $reportPath -Raw
        
        # Extract recommendation using regex pattern
        $recommendationPattern = '<span class="([^"]+)">([^<]+)<\/span>'
        $match = [regex]::Match($content, $recommendationPattern)
        
        if ($match.Success) {
            $recommendationClass = $match.Groups[1].Value
            $recommendationText = $match.Groups[2].Value
            
            $results[$ticker] = @{
                "RecommendationClass" = $recommendationClass
                "RecommendationText" = $recommendationText
            }
        }
    }
}

# Output to JSON file
$results | ConvertTo-Json -Depth 3 | Out-File -FilePath "c:\Development\Altman-Z-Score-1\actual_recommendations.json" -Encoding utf8

# Output strong buys to console
Write-Host "Companies with STRONG BUY recommendations:"
$strongBuys = $results.GetEnumerator() | Where-Object { $_.Value.RecommendationText -eq "Strong Buy" }
foreach ($item in $strongBuys) {
    Write-Host "$($item.Key): $($item.Value.RecommendationText)"
}

Write-Host "`nTotal STRONG BUY companies: $($strongBuys.Count)"

# Create a simplified JSON with just the strong buys
$strongBuysJson = @{}
foreach ($item in $strongBuys) {
    $strongBuysJson[$item.Key] = $item.Value.RecommendationText
}

$strongBuysJson | ConvertTo-Json | Out-File -FilePath "c:\Development\Altman-Z-Score-1\strong_buys.json" -Encoding utf8
