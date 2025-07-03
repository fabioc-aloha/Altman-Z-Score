# ===============================================================================
# Altman Z-Score Dashboard Generator (PowerShell)
# Handles file operations and launches Python dashboard generator
# Compatible with PowerShell 5.1+ and PowerShell Core 6+
# ===============================================================================

<#
.SYNOPSIS
    Handles file operations and launches Python dashboard generator for Altman Z-Score analysis.

.DESCRIPTION
    This script prepares the environment and assets, then calls the Python dashboard 
    generator to create a modern, interactive dashboard. It handles:
    1. Creating necessary directories
    2. Copying required assets (CSS, JS, logos)
    3. Calling the Python script for data processing and HTML generation
    4. Opening the dashboard in the default browser

.EXAMPLE
    .\generate_web.ps1
    Generates the dashboard and opens it in the browser.

.EXAMPLE
    .\generate_web.ps1 -Verbose
    Generates dashboard with detailed output.

.EXAMPLE
    .\generate_web.ps1 -SkipDataCopy
    Generates dashboard without copying analysis output data (uses existing web/output/).

.PARAMETER SkipDataCopy
    Skip copying analysis output data from main output/ directory to web/output/.
    Useful when data is already up-to-date or for faster iterations during development.
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$SkipDataCopy,
    
    [Parameter()]
    [switch]$Help
)

#Requires -Version 5.1

# Set error action preference
$ErrorActionPreference = "Continue"

# Define colors for output
$script:Colors = @{
    Header   = "Cyan"
    Success  = "Green"
    Error    = "Red"
    Warning  = "Yellow"
    Info     = "White"
    Debug    = "Gray"
    Emphasis = "Magenta"
    Status   = "DarkGray"
}

function Write-ColorText {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Text,
        
        [Parameter(Position = 1)]
        [ValidateSet("Header", "Success", "Error", "Warning", "Info", "Debug", "Emphasis", "Status")]
        [string]$Color = "Info",

        [Parameter()]
        [switch]$ShowAlways
    )
    
    # Only show Info and Debug messages if -Verbose is specified or ShowAlways is true
    if ($ShowAlways -or 
        $Color -notin @("Info", "Debug") -or 
        ($VerbosePreference -eq 'Continue' -and ($Color -in @("Info", "Debug") -or $Text -match '^\[(?:INFO|DEBUG)\]'))) {
        Write-Host $Text -ForegroundColor $script:Colors[$Color]
    }
}

function Write-Header {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Title
    )
    
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor $script:Colors.Header
    Write-Host (" " * [math]::Floor((80 - $Title.Length) / 2)) + $Title -ForegroundColor $script:Colors.Header
    Write-Host ("=" * 80) -ForegroundColor $script:Colors.Header
    Write-Host ""
}

function Copy-DashboardAssets {
    [CmdletBinding()]
    param(
        [Parameter()]
        [switch]$SkipDataCopy
    )
    
    Write-ColorText "[1/4] Preparing output directories and assets..." "Info" -ShowAlways
    
    # Create output directories if they don't exist
    $webDir = Join-Path $PSScriptRoot "web"
    if (-not (Test-Path $webDir)) {
        New-Item -ItemType Directory -Path $webDir | Out-Null
        Write-ColorText "  [OK] Created web directory" "Success"
    }

    $webOutputDir = Join-Path $webDir "output"
    if (-not (Test-Path $webOutputDir)) {
        New-Item -ItemType Directory -Path $webOutputDir | Out-Null
        Write-ColorText "  [OK] Created web/output directory" "Success"
    }

    Write-ColorText "[2/4] Copying analysis output data..." "Info" -ShowAlways
    
    if ($SkipDataCopy) {
        Write-ColorText "  [SKIPPED] Data copy bypassed (using existing web/output/ data)" "Warning" -ShowAlways
    }
    else {
        # Copy analysis output data from main output directory
        $mainOutputDir = Join-Path $PSScriptRoot "output"
        if (Test-Path $mainOutputDir) {
            # Copy all company directories and their contents
            $companyDirs = Get-ChildItem -Path $mainOutputDir -Directory
            $copiedCount = 0
            
            foreach ($companyDir in $companyDirs) {
                $destCompanyDir = Join-Path $webOutputDir $companyDir.Name
                
                # Create company directory in web/output if it doesn't exist
                if (-not (Test-Path $destCompanyDir)) {
                    New-Item -ItemType Directory -Path $destCompanyDir | Out-Null
                }
                
                # Copy all files from the company directory
                $files = Get-ChildItem -Path $companyDir.FullName -File
                foreach ($file in $files) {
                    $destFile = Join-Path $destCompanyDir $file.Name
                    Copy-Item -Path $file.FullName -Destination $destFile -Force
                }
                $copiedCount++
            }
            
            if ($copiedCount -gt 0) {
                Write-ColorText "  [OK] Copied analysis data for $copiedCount companies" "Success"
            }
            else {
                Write-ColorText "  [WARNING] No company analysis data found in output directory" "Warning"
            }
        }
        else {
            Write-ColorText "  [WARNING] Main output directory not found. Run analysis first to generate data." "Warning" -ShowAlways
        }
    }

    Write-ColorText "[3/4] Copying dashboard assets..." "Info" -ShowAlways

    # Copy only essential assets (logo for fallback and favicon)
    $assetsToMove = @(
        @{
            Source = "default_logo.png"
            Dest   = "web/default_logo.png"
        },
        @{
            Source = "favicon.svg"
            Dest   = "web/favicon.svg"
        }
    )

    foreach ($asset in $assetsToMove) {
        $sourcePath = Join-Path $PSScriptRoot $asset.Source
        $destPath = Join-Path $PSScriptRoot $asset.Dest
        if (Test-Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            Write-ColorText "  [OK] Copied $($asset.Source) to web directory" "Success"
        }
        else {
            Write-ColorText "  [WARNING] Could not find $($asset.Source)" "Warning"
        }
    }
}

# Main script execution
try {
    # Show help if requested
    if ($Help) {
        Get-Help $MyInvocation.MyCommand.Path -Full
        return 0
    }

    Write-Header "Altman Z-Score Dashboard Generator"
    
    # Copy required assets
    Copy-DashboardAssets -SkipDataCopy:$SkipDataCopy
    
    # Call Python script to generate dashboard
    Write-ColorText "[4/4] Generating dashboard..." "Info" -ShowAlways
    [System.Collections.ArrayList]$pythonArgs = @(
        "scripts/generate_dashboard.py",
        "--output-dir",
        "web"
    )
    if ($VerbosePreference -eq 'Continue') {
        [void]$pythonArgs.Add("--verbose")
    }
    
    # Execute Python script with proper error handling
    $pythonOutput = & python $pythonArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        # Display Python error output in red
        Write-ColorText "Python script failed with the following error:" "Error" -ShowAlways
        foreach ($line in $pythonOutput) {
            Write-ColorText $line "Error" -ShowAlways
        }
        throw "Python script failed with exit code $LASTEXITCODE"
    }
    elseif ($VerbosePreference -eq 'Continue') {
        # In verbose mode, show Python output
        foreach ($line in $pythonOutput) {
            Write-ColorText $line "Debug"
        }
    }
    
    # Verify dashboard was generated
    $dashboardPath = Join-Path $PSScriptRoot "web/dashboard.html"
    if (-not (Test-Path $dashboardPath)) {
        throw "Dashboard file was not generated at $dashboardPath"
    }
    
    if (Test-Path $dashboardPath) {
        # Open dashboard in browser
        Write-ColorText "[OK] Opening dashboard in browser..." "Info" -ShowAlways
        Start-Process $dashboardPath
            
        Write-Host ""
        Write-Host ("------------------------------------------------------------") -ForegroundColor $script:Colors.Status
        Write-Host ("Generation Complete") -ForegroundColor $script:Colors.Success
        Write-Host ("------------------------------------------------------------") -ForegroundColor $script:Colors.Status
        Write-ColorText "[SUCCESS] Dashboard generated successfully!" "Success"
        Write-Host "OUTPUT: $dashboardPath" -ForegroundColor Cyan
        Write-Host "FEATURES:" -ForegroundColor Cyan
        Write-Host "* Self-contained HTML with embedded CSS and JavaScript" -ForegroundColor $script:Colors.Status
        Write-Host "* Advanced filtering by model, risk category, and recommendation" -ForegroundColor $script:Colors.Status
        Write-Host "* Real-time search across symbols and company names" -ForegroundColor $script:Colors.Status
        Write-Host "* Sortable columns with visual indicators" -ForegroundColor $script:Colors.Status
        Write-Host "* Responsive design for mobile and desktop" -ForegroundColor $script:Colors.Status
        Write-Host "* Color-coded Z-Scores and recommendations" -ForegroundColor $script:Colors.Status
        Write-Host "* Perfect for filesystem usage (file:// protocol)" -ForegroundColor $script:Colors.Status
    }
    else {
        throw "Dashboard file not found at: $dashboardPath"
    }
}
catch {
    Write-ColorText "[ERROR] An error occurred: $($_.Exception.Message)" "Error"
    Write-Verbose "Stack trace: $($_.ScriptStackTrace)"
    return 1
}

return 0
