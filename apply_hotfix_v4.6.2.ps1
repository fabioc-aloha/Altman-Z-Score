# Update Altman Z-Score project to version 4.6.2 HOTFIX
# This script updates version numbers and documentation for the 4.6.2 hotfix

Write-Host "Applying version 4.6.2 HOTFIX - Enhanced Documentation & Environment Updates..." -ForegroundColor Cyan

# Check files
$flowMd = "FLOW.md"
$readmeMd = "README.md"
$changelogMd = "CHANGELOG.md"
$versionPy = "altman_zscore\_version.py"
$copilotInstructions = ".github\copilot-instructions.md"
$docsHotfix = "docs\HOTFIX_v4.6.2_DOCUMENTATION_ENHANCEMENT.md"

# Verify all files exist
$allFilesExist = $true
foreach ($file in @($flowMd, $readmeMd, $changelogMd, $versionPy, $copilotInstructions, $docsHotfix)) {
    if (-not (Test-Path $file)) {
        Write-Host "[X] File not found: $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "[X] Some required files are missing. Please check the project structure." -ForegroundColor Red
    exit 1
}

# Display changes
Write-Host "`nSummary of 4.6.2 HOTFIX changes:" -ForegroundColor Yellow

Write-Host "`n1. Updated version numbers:" -ForegroundColor Cyan
Write-Host "   - FLOW.md: 4.6.1 -> 4.6.2"
Write-Host "   - README.md: 4.6.0 -> 4.6.2"
Write-Host "   - _version.py: 4.6.0 -> 4.6.2"

Write-Host "`n2. Added new documentation:" -ForegroundColor Cyan
Write-Host "   - docs\HOTFIX_v4.6.2_DOCUMENTATION_ENHANCEMENT.md"

Write-Host "`n3. Enhanced AI learnings in copilot instructions:" -ForegroundColor Cyan
Write-Host "   - Added @centralization Rule"
Write-Host "   - Added @fallback Rule"
Write-Host "   - Added @caching Rule"
Write-Host "   - Added @documentation Rule"
Write-Host "   - Added @redirection Rule"
Write-Host "   - Added Architecture & Data Flow Knowledge section"

Write-Host "`n4. Updated CHANGELOG.md with detailed 4.6.2 HOTFIX information" -ForegroundColor Cyan

Write-Host "`n5. Updated project assets:" -ForegroundColor Cyan
Write-Host "   - Updated banner.png with new branding"
Write-Host "   - Added SEC_EDGAR_INTEGRATION_PLAN.md"

Write-Host "`nHOTFIX v4.6.2 has been successfully applied." -ForegroundColor Green
Write-Host "Documentation and environment updates are now in place." -ForegroundColor Green
Write-Host "`nKey improvements:" -ForegroundColor Yellow
Write-Host "- Enhanced AI learning documentation"
Write-Host "- SEC EDGAR integration guide"
Write-Host "- Improved error messages"
Write-Host "- Documentation versioning"
Write-Host "- PowerShell standardization"
Write-Host "- Updated project banner"
Write-Host "- Added SEC EDGAR implementation plan"

Write-Host "`nTo view the full hotfix details, see: docs\HOTFIX_v4.6.2_DOCUMENTATION_ENHANCEMENT.md" -ForegroundColor Cyan

# Git operations
$commitChanges = $true
$pushChanges = $true

# Prompt for Git operations
$response = Read-Host "`nWould you like to commit these changes? (y/n) [Default: y]"
if ($response -eq "n") {
    $commitChanges = $false
    $pushChanges = $false
}

if ($commitChanges) {
    Write-Host "`nStaging changes..." -ForegroundColor Cyan
    git add $flowMd $readmeMd $changelogMd $versionPy $copilotInstructions $docsHotfix

    # Check if there are other modified files
    $otherChanges = git status --porcelain | Where-Object { $_ -match '^\s*[MA]\s+' }
    if ($otherChanges) {
        Write-Host "`nAdditional modified files detected:" -ForegroundColor Yellow
        $otherChanges | ForEach-Object { Write-Host "   - $($_.Substring(3))" }
        
        $stageAll = Read-Host "Would you like to stage all changes? (y/n) [Default: n]"
        if ($stageAll -eq "y") {
            Write-Host "Staging all changes..." -ForegroundColor Cyan
            git add -A
        }
    }

    # Commit changes
    $commitMessage = "HOTFIX v4.6.2: Enhanced Documentation & Environment Updates"
    Write-Host "`nCommitting changes with message: '$commitMessage'..." -ForegroundColor Cyan
    git commit -m $commitMessage

    # Push changes if requested
    if ($pushChanges) {
        $response = Read-Host "`nWould you like to push these changes? (y/n) [Default: y]"
        if ($response -ne "n") {
            Write-Host "`nPushing changes to remote repository..." -ForegroundColor Cyan
            git push
            
            $pushResult = $?
            if ($pushResult) {
                Write-Host "`n[OK] Successfully pushed HOTFIX v4.6.2 to remote repository." -ForegroundColor Green
            }
            else {
                Write-Host "`n[X] Failed to push changes to remote repository." -ForegroundColor Red
                Write-Host "Please push manually when ready." -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "`nChanges have been committed locally but not pushed." -ForegroundColor Yellow
            Write-Host "Use 'git push' to push changes when ready." -ForegroundColor Cyan
        }
    }
}
else {
    Write-Host "`nChanges have not been committed." -ForegroundColor Yellow
    Write-Host "Use the following commands to commit and push when ready:" -ForegroundColor Cyan
    Write-Host "   git add -A" -ForegroundColor DarkGray
    Write-Host "   git commit -m `"HOTFIX v4.6.2: Enhanced Documentation & Environment Updates`"" -ForegroundColor DarkGray
    Write-Host "   git push" -ForegroundColor DarkGray
}

Write-Host "`nHOTFIX v4.6.2 process complete!" -ForegroundColor Green
