[CmdletBinding()]
param(
    [string]$Path = ".",
    [switch]$IncludeHidden,
    [switch]$Detailed
)

function Find-EmptyFiles {
    [CmdletBinding()]
    param(
        [string]$SearchPath,
        [bool]$IncludeHidden,
        [bool]$ShowDetailed
    )
    
    Write-Host "Searching for empty files in: $SearchPath" -ForegroundColor Cyan
    Write-Host "Include hidden files: $IncludeHidden" -ForegroundColor Gray
    Write-Host "=" * 50 -ForegroundColor Gray
    
    $emptyFiles = @()
    $totalFiles = 0
    $totalSize = 0
    
    # Get all files recursively
    $files = Get-ChildItem -Path $SearchPath -File -Recurse -Force:$IncludeHidden
    
    foreach ($file in $files) {
        $totalFiles++
        $totalSize += $file.Length
        
        if ($file.Length -eq 0) {
            $emptyFiles += $file
            
            if ($ShowDetailed) {
                Write-Host "EMPTY: $($file.FullName)" -ForegroundColor Red
                Write-Host "  Created: $($file.CreationTime)" -ForegroundColor Yellow
                Write-Host "  Modified: $($file.LastWriteTime)" -ForegroundColor Yellow
                Write-Host ""
            }
            else {
                Write-Host "EMPTY: $($file.FullName)" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "=" * 50 -ForegroundColor Gray
    Write-Host "SUMMARY:" -ForegroundColor Cyan
    Write-Host "Total files scanned: $totalFiles" -ForegroundColor Green
    Write-Host "Empty files found: $($emptyFiles.Count)" -ForegroundColor $(if ($emptyFiles.Count -gt 0) { "Red" } else { "Green" })
    Write-Host "Total size of all files: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Green
    
    if ($emptyFiles.Count -gt 0) {
        Write-Host "" -ForegroundColor Yellow
        Write-Host "EMPTY FILES BY DIRECTORY:" -ForegroundColor Yellow
        $emptyFiles | Group-Object { $_.Directory.FullName } | Sort-Object Name | ForEach-Object {
            Write-Host "  $($_.Name):" -ForegroundColor Yellow
            $_.Group | Sort-Object Name | ForEach-Object {
                Write-Host "    $($_.Name)" -ForegroundColor Red
            }
        }
        
        Write-Host "" -ForegroundColor Yellow
        Write-Host "RECOMMENDATION:" -ForegroundColor Yellow
        Write-Host "Review these empty files to determine if they should be:" -ForegroundColor Yellow
        Write-Host "  - Deleted (if they are obsolete or accidental)" -ForegroundColor Yellow
        Write-Host "  - Populated with content (if they serve a purpose)" -ForegroundColor Yellow
        Write-Host "  - Kept as placeholders (if they are intentional)" -ForegroundColor Yellow
    }
    else {
        Write-Host "No empty files found - project is clean! [OK]" -ForegroundColor Green
    }
    
    return @{
        EmptyFiles = $emptyFiles
        TotalFiles = $totalFiles
        TotalSize  = $totalSize
    }
}

# Main execution
try {
    $result = Find-EmptyFiles -SearchPath $Path -IncludeHidden:$IncludeHidden -ShowDetailed:$Detailed
    
    if ($result.EmptyFiles.Count -gt 0) {
        exit 1  # Exit with error code if empty files found
    }
    else {
        exit 0  # Exit successfully if no empty files
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 2
}
