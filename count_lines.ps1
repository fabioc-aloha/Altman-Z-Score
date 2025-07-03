# Script to count lines of code and documentation
# This script counts lines in Python (.py), PowerShell (.ps1), and Markdown (.md) files

$workspaceRoot = Get-Location

Write-Host "Altman Z-Score Project - Line Count Analysis" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Initialize counters
$totalPythonLines = 0
$totalPowerShellLines = 0
$totalMarkdownLines = 0
$totalPythonFiles = 0
$totalPowerShellFiles = 0
$totalMarkdownFiles = 0

# Function to get line count in a file
function Get-LineCount {
    param (
        [string]$FilePath
    )
    try {
        $content = Get-Content $FilePath -ErrorAction Stop
        if ($content) {
            return $content.Count
        }
        else {
            return 0
        }
    }
    catch {
        Write-Warning "Could not read file: $FilePath"
        return 0
    }
}

# Count Python files (.py)
Write-Host "Analyzing Python files (.py)..." -ForegroundColor Yellow
$pythonFiles = Get-ChildItem -Path $workspaceRoot -Recurse -Filter "*.py" -File | Where-Object { 
    $_.FullName -notlike "*\__pycache__\*" -and 
    $_.FullName -notlike "*\.venv\*" -and 
    $_.FullName -notlike "*\venv\*" -and
    $_.FullName -notlike "*\node_modules\*"
}

foreach ($file in $pythonFiles) {
    $lineCount = Get-LineCount -FilePath $file.FullName
    $totalPythonLines += $lineCount
    $totalPythonFiles++
    $relativePath = $file.FullName.Replace($workspaceRoot, "").TrimStart('\')
    Write-Host "  $relativePath : $lineCount lines" -ForegroundColor Gray
}

# Count PowerShell files (.ps1)
Write-Host ""
Write-Host "Analyzing PowerShell files (.ps1)..." -ForegroundColor Yellow
$powerShellFiles = Get-ChildItem -Path $workspaceRoot -Recurse -Filter "*.ps1" -File

foreach ($file in $powerShellFiles) {
    $lineCount = Get-LineCount -FilePath $file.FullName
    $totalPowerShellLines += $lineCount
    $totalPowerShellFiles++
    $relativePath = $file.FullName.Replace($workspaceRoot, "").TrimStart('\')
    Write-Host "  $relativePath : $lineCount lines" -ForegroundColor Gray
}

# Count Markdown files (.md)
Write-Host ""
Write-Host "Analyzing Markdown documentation files (.md)..." -ForegroundColor Yellow
$markdownFiles = Get-ChildItem -Path $workspaceRoot -Recurse -Filter "*.md" -File

foreach ($file in $markdownFiles) {
    $lineCount = Get-LineCount -FilePath $file.FullName
    $totalMarkdownLines += $lineCount
    $totalMarkdownFiles++
    $relativePath = $file.FullName.Replace($workspaceRoot, "").TrimStart('\')
    Write-Host "  $relativePath : $lineCount lines" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "SUMMARY" -ForegroundColor Green
Write-Host "=======" -ForegroundColor Green
Write-Host ""
Write-Host "Code Files:" -ForegroundColor Cyan
Write-Host "  Python files (.py): $totalPythonFiles files, $totalPythonLines lines" -ForegroundColor White
Write-Host "  PowerShell files (.ps1): $totalPowerShellFiles files, $totalPowerShellLines lines" -ForegroundColor White
Write-Host "  Total Code Lines: $($totalPythonLines + $totalPowerShellLines)" -ForegroundColor Yellow

Write-Host ""
Write-Host "Documentation Files:" -ForegroundColor Cyan
Write-Host "  Markdown files (.md): $totalMarkdownFiles files, $totalMarkdownLines lines" -ForegroundColor White

Write-Host ""
Write-Host "PROJECT TOTALS:" -ForegroundColor Magenta
Write-Host "  Total Files: $($totalPythonFiles + $totalPowerShellFiles + $totalMarkdownFiles)" -ForegroundColor White
Write-Host "  Total Lines: $($totalPythonLines + $totalPowerShellLines + $totalMarkdownLines)" -ForegroundColor White
Write-Host "  Code/Documentation Ratio: $([math]::Round(($totalPythonLines + $totalPowerShellLines) / $totalMarkdownLines, 2)):1" -ForegroundColor White

# Additional file type analysis
Write-Host ""
Write-Host "OTHER FILE TYPES:" -ForegroundColor Cyan
$otherExtensions = @('.txt', '.bat', '.ini', '.toml')
foreach ($ext in $otherExtensions) {
    $files = Get-ChildItem -Path $workspaceRoot -Recurse -Filter "*$ext" -File | Where-Object { 
        $_.FullName -notlike "*\__pycache__\*" -and 
        $_.FullName -notlike "*\.venv\*" -and 
        $_.FullName -notlike "*\venv\*" -and
        $_.FullName -notlike "*\node_modules\*"
    }
    if ($files.Count -gt 0) {
        $totalLines = 0
        foreach ($file in $files) {
            $totalLines += Get-LineCount -FilePath $file.FullName
        }
        Write-Host "  $ext files: $($files.Count) files, $totalLines lines" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Analysis complete!" -ForegroundColor Green
