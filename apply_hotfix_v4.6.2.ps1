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

Write-Host "`nHOTFIX v4.6.2 has been successfully applied." -ForegroundColor Green
Write-Host "Documentation and environment updates are now in place." -ForegroundColor Green
Write-Host "`nKey improvements:" -ForegroundColor Yellow
Write-Host "- Enhanced AI learning documentation"
Write-Host "- SEC EDGAR integration guide"
Write-Host "- Improved error messages"
Write-Host "- Documentation versioning"
Write-Host "- PowerShell standardization"

Write-Host "`nTo view the full hotfix details, see: docs\HOTFIX_v4.6.2_DOCUMENTATION_ENHANCEMENT.md" -ForegroundColor Cyan

# Git operations - commit and push
Write-Host "`n=== Git Operations ===" -ForegroundColor Yellow
Write-Host "Would you like to commit and push these changes? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "`nPerforming Git operations..." -ForegroundColor Cyan
    
    # Check if git is available
    try {
        $gitVersion = git --version
        Write-Host "[OK] Git detected: $gitVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "[X] Git not found. Please install Git or add it to your PATH." -ForegroundColor Red
        exit 1
    }
    
    # Check if we're in a git repository
    try {
        $gitStatus = git status --porcelain
        Write-Host "[OK] Git repository detected" -ForegroundColor Green
    }
    catch {
        Write-Host "[X] Not a git repository. Please run this script from the root of the git repository." -ForegroundColor Red
        exit 1
    }
    
    # Stage all changes
    try {
        Write-Host "Staging changes..." -ForegroundColor Cyan
        git add .
        Write-Host "[OK] Changes staged successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "[X] Failed to stage changes: $_" -ForegroundColor Red
        exit 1
    }
    
    # Commit changes
    try {
        Write-Host "Committing changes..." -ForegroundColor Cyan
        git commit -m "HOTFIX v4.6.2: Enhanced Documentation & Environment Updates"
        Write-Host "[OK] Changes committed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "[X] Failed to commit changes: $_" -ForegroundColor Red
        exit 1
    }
    
    # Prompt for push
    Write-Host "Push changes to remote repository? (Y/N)" -ForegroundColor Cyan
    $pushResponse = Read-Host
    
    if ($pushResponse -eq "Y" -or $pushResponse -eq "y") {
        try {
            Write-Host "Pushing changes to remote repository..." -ForegroundColor Cyan
            git push
            Write-Host "[OK] Changes pushed successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "[X] Failed to push changes: $_" -ForegroundColor Red
            Write-Host "You may need to push manually using 'git push'" -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        Write-Host "Changes have been committed locally but not pushed." -ForegroundColor Yellow
        Write-Host "Use 'git push' to push the changes when ready." -ForegroundColor Cyan
    }
    
    Write-Host "`nHOTFIX v4.6.2 has been successfully applied and versioned in Git." -ForegroundColor Green
}
else {
    Write-Host "`nChanges have been applied but not committed to Git." -ForegroundColor Yellow
    Write-Host "To manually commit the changes, use:" -ForegroundColor Cyan
    Write-Host "git add ." -ForegroundColor Gray
    Write-Host "git commit -m 'HOTFIX v4.6.2: Enhanced Documentation & Environment Updates'" -ForegroundColor Gray
    Write-Host "git push" -ForegroundColor Gray
}
