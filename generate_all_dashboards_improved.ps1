# ===============================================================================
# Altman Z-Score Stock Picks Dashboard Generator (PowerShell)
# This script generates all stock recommendation dashboards
# Compatible with PowerShell 5.1+ and PowerShell Core 6+
# ===============================================================================

<#
.SYNOPSIS
    Generates HTML dashboards for Altman Z-Score stock analysis.

.DESCRIPTION
    This script runs a series of Python scripts to generate interactive HTML dashboards
    for different investor profiles and recommendation types based on Altman Z-Score analysis.

.PARAMETER OpenBrowser
    Whether to open the main dashboard in the default browser after generation.
    Default: $true

.PARAMETER Verbose
    Show detailed output including descriptions for each step.

.PARAMETER NoPause
    Skip the "Press any key to continue" prompt at the end.
    
.PARAMETER NoCopy
    Skip copying files from output/ to web/output/ directory.

.EXAMPLE
    .\generate_all_dashboards.ps1
    Generates all dashboards and opens the main page in browser.

.EXAMPLE
    .\generate_all_dashboards.ps1 -Verbose -NoPause
    Generates dashboards with detailed output and exits immediately.

.EXAMPLE
    .\generate_all_dashboards.ps1 -OpenBrowser:$false
    Generates dashboards without opening browser.
    
.EXAMPLE
    .\generate_all_dashboards.ps1 -NoCopy
    Generates dashboards without copying output files to web/output/ directory.
#>

#Requires -Version 5.1

param(
    [switch]$OpenBrowser,
    [switch]$Verbose,
    [switch]$NoPause,
    [switch]$NoCopy
)

# Set error action preference
$ErrorActionPreference = "Continue"

# Initialize Python command variable
$script:PythonCommand = "python"

# Check execution policy on Windows
if ($IsWindows -or ($PSVersionTable.PSVersion.Major -lt 6)) {
    $executionPolicy = Get-ExecutionPolicy
    if ($executionPolicy -eq 'Restricted') {
        Write-Warning "PowerShell execution policy is Restricted. You may need to run:"
        Write-Warning "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        Write-Warning "Or run with: pwsh -ExecutionPolicy Bypass -File generate_all_dashboards.ps1"
    }
}

# Define colors for output - compatible with both Windows PowerShell and PowerShell Core
$Colors = @{
    Header   = "Cyan"
    Success  = "Green"
    Error    = "Red"
    Warning  = "Yellow"
    Info     = "White"
    Emphasis = "Magenta"
}

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

function Write-Header {
    param([string]$Title)
    
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor $Colors.Header
    Write-Host (" " * [math]::Floor((80 - $Title.Length) / 2)) + $Title -ForegroundColor $Colors.Header
    Write-Host ("=" * 80) -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    
    Write-Host ""
    Write-Host ("-" * 80) -ForegroundColor $Colors.Info
    Write-Host $Title -ForegroundColor $Colors.Emphasis
    Write-Host ("-" * 80) -ForegroundColor $Colors.Info
}

function Invoke-PythonScript {
    param(
        [string]$ScriptPath,
        [string]$Description,
        [int]$StepNumber,
        [int]$TotalSteps
    )
    
    # Display a single line for the task that's starting
    Write-Host "[$StepNumber/$TotalSteps] " -NoNewline -ForegroundColor $Colors.Info
    Write-Host "Processing: " -NoNewline -ForegroundColor $Colors.Info
    Write-Host $Description -NoNewline -ForegroundColor $Colors.Emphasis
    Write-Host " ... " -NoNewline -ForegroundColor $Colors.Info
    
    if ($Verbose) {
        Write-Host ""
        Write-Host "    Command: $ScriptPath" -ForegroundColor $Colors.Info
        Write-Host "    Description: $Description" -ForegroundColor $Colors.Info
    }
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    try {
        # Split the ScriptPath into script name and arguments
        $scriptParts = $ScriptPath -split ' ', 2
        $scriptName = $scriptParts[0]
        $scriptArgs = if ($scriptParts.Count -gt 1) { $scriptParts[1] } else { $null }
        
        # Capture script output but don't display it unless there's an error or verbose mode is on
        if ($scriptArgs) {
            $result = & $script:PythonCommand $scriptName $scriptArgs 2>&1
        }
        else {
            $result = & $script:PythonCommand $scriptName 2>&1
        }
        
        $exitCode = $LASTEXITCODE
        
        $stopwatch.Stop()
        $duration = $stopwatch.Elapsed.TotalSeconds
        
        if ($exitCode -eq 0) {
            # Complete the line that was started above
            Write-Host "✅ " -NoNewline -ForegroundColor $Colors.Success
            Write-Host "($([math]::Round($duration, 2))s)" -ForegroundColor $Colors.Info
            return $true
        }
        else {
            # If there's an error, complete the line with an error indicator
            Write-Host "❌ " -ForegroundColor $Colors.Error
            
            # Add detailed error information on the next lines
            Write-Host "    ERROR: Failed to generate $Description" -ForegroundColor $Colors.Error
            
            if ($result) {
                # Always show output on error, but limit it to avoid excessive output
                $truncatedResult = if ($result.Length -gt 500) { $result.Substring(0, 500) + "..." } else { $result }
                Write-Host "    Output: $truncatedResult" -ForegroundColor $Colors.Warning
            }
            return $false
        }
    }
    catch {
        $stopwatch.Stop()
        
        # If there's an exception, complete the line with an error indicator
        Write-Host "❌ " -ForegroundColor $Colors.Error
        
        # Add detailed error information on the next lines
        Write-Host "    EXCEPTION: $($_.Exception.Message)" -ForegroundColor $Colors.Error
        return $false
    }
}

function Test-PythonAvailable {
    $pythonCommands = @('python', 'python3', 'py')
    
    foreach ($cmd in $pythonCommands) {
        try {
            $pythonVersion = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✅ Python detected ($cmd): $pythonVersion" "Success"
                $script:PythonCommand = $cmd
                return $true
            }
        }
        catch {
            # Continue to next command
        }
    }
    
    Write-ColorText "❌ Python not found. Tried: $($pythonCommands -join ', ')" "Error"
    Write-ColorText "💡 Please install Python and ensure it's in your PATH" "Info"
    return $false
}

function Get-DashboardFiles {
    $webDir = Join-Path $PSScriptRoot "web"
    
    # Define names for known dashboards
    $knownDashboards = @{
        "index.html"                       = "Main Navigation";
        "strong_buys.html"                 = "Strong Buys";
        "conservative_picks.html"          = "Conservative Picks";
        "dividend_picks.html"              = "Dividend Picks";
        "value_picks.html"                 = "Value Picks";
        "growth_picks.html"                = "Growth Picks";
        "aggressive_picks.html"            = "Aggressive Picks";
        "sell_picks.html"                  = "Sell Recommendations";
        "strong_sell_picks.html"           = "Strong Sell Recommendations";
        "manufacturing_&_industrial.html"  = "Manufacturing & Industrial";
        "private_&_service_companies.html" = "Private & Service Companies";
        "emerging_markets.html"            = "Emerging Markets";
        "financial_institutions.html"      = "Financial Institutions";
        "regulated_utilities.html"         = "Regulated Utilities";
        "technology_&_growth.html"         = "Technology & Growth";
        "retail_&_consumer.html"           = "Retail & Consumer";
        "model_portfolios_index.html"      = "Model Portfolios Index";
    }
    
    $dashboards = @()
    
    # Dynamically find all HTML files in the web directory
    Get-ChildItem -Path $webDir -Filter "*.html" -File | ForEach-Object {
        $fileName = $_.Name
        
        # Use known name if available, otherwise format the filename
        if ($knownDashboards.ContainsKey($fileName)) {
            $displayName = $knownDashboards[$fileName]
        }
        else {
            $displayName = $fileName -replace "\.html$", "" -replace "_", " " -replace "-", " "
            $displayName = (Get-Culture).TextInfo.ToTitleCase($displayName)
        }
        
        $dashboards += @{ 
            File = $_.FullName
            Name = $displayName
        }
    }
    
    return $dashboards
}

# Main execution starts here
Clear-Host
Write-Header "Altman Z-Score Stock Picks Dashboard Generator"

# Set default for OpenBrowser if not specified
if (-not $PSBoundParameters.ContainsKey('OpenBrowser')) {
    $OpenBrowser = $true
}

Write-ColorText "🚀 Starting dashboard generation process..." "Info"
Write-ColorText "📋 Process Flow: Assets → Templates → Dashboards → Navigation" "Info"
Write-Host ""

# Check if Python is available
if (-not (Test-PythonAvailable)) {
    Write-ColorText "Please ensure Python is installed and available in your PATH." "Error"
    if (-not $NoPause) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

Write-Host ""

# Define the scripts to run - Enhanced with modern styling and better logo handling
$scriptsDir = Join-Path $PSScriptRoot "scripts\utilities"
$scripts = @(
    # First run the enhanced portfolio generation scripts - using the "all" option for modern styling
    @{ Path = "$(Join-Path $scriptsDir "generate_portfolio_enhanced.py") all"; Description = "Enhanced Portfolio Dashboards with Modern Styling & Logo Handling" },
    # Generate special dashboards using standardized templates and styles
    @{ Path = "$(Join-Path $scriptsDir "generate_special_dashboards_standardized.py")"; Description = "Enhanced Special Dashboards (Strong Buy/Sell)" },
    # Use the standardized model portfolios generator for consistent styling across all dashboards
    @{ Path = "$(Join-Path $scriptsDir "generate_model_portfolios_standardized.py")"; Description = "Enhanced Model Portfolios" },
    # Generate the enhanced main navigation page (after all other dashboards are created)
    @{ Path = "$(Join-Path $scriptsDir "generate_main_page_enhanced.py")"; Description = "Enhanced Main Navigation Page" },
    # Fix any HTML files that might still reference old CSS files
    @{ Path = "$(Join-Path $scriptsDir "fix_html_css_references.py")"; Description = "Fix CSS References" }
)

# PowerShell scripts to run after Python scripts (currently none needed since CSS is embedded during generation)
$powershellScripts = @(
    # CSS is now embedded directly during HTML generation, so no post-processing needed
)

# Initialize counters
$totalScripts = $scripts.Count
$successCount = 0
$failedScripts = @()

# Ensure web directory exists
$webDir = Join-Path $PSScriptRoot "web"
if (-not (Test-Path $webDir)) {
    Write-ColorText "Creating web directory for output..." "Info"
    New-Item -Path $webDir -ItemType Directory -Force | Out-Null
}

# Define output and web output directories
$outputDir = Join-Path $PSScriptRoot "output"
$webOutputDir = Join-Path $webDir "output"

# Just ensure the web/output directory exists, but don't copy yet - we'll do it once after all scripts run
if (-not (Test-Path $webOutputDir)) {
    Write-ColorText "Creating web/output directory for generated assets..." "Info"
    New-Item -Path $webOutputDir -ItemType Directory -Force | Out-Null
}

if (-not (Test-Path $outputDir)) {
    Write-ColorText "⚠️ Output directory not found: $outputDir" "Warning"
}

# Step 1: Copy assets from output/ to web/output/ FIRST (unless NoCopy is specified)
# This ensures all company data and logos are available for dashboard generation
if (-not $NoCopy) {
    Write-Section "Preparing Assets"
    Write-Host "📂 " -NoNewline -ForegroundColor $Colors.Info
    Write-Host "Copying assets from output/ to web/output/..." -ForegroundColor $Colors.Info

    if (Test-Path $outputDir) {
        # Create web/output directory if it doesn't exist
        if (-not (Test-Path $webOutputDir)) {
            New-Item -Path $webOutputDir -ItemType Directory -Force | Out-Null
        }
        
        # Copy only .html, .png, and .txt files from output/ to web/output/
        $fileCount = 0
        Get-ChildItem -Path $outputDir -Include "*.html", "*.png", "*.txt" -Recurse | ForEach-Object {
            $destPath = $_.FullName.Replace($outputDir, $webOutputDir)
            $destDir = Split-Path -Path $destPath -Parent
            
            if (-not (Test-Path $destDir)) {
                New-Item -Path $destDir -ItemType Directory -Force | Out-Null
            }
            
            Copy-Item -Path $_.FullName -Destination $destPath -Force
            $fileCount++
        }
        
        Write-ColorText "✅ Successfully copied $fileCount files (html, png, txt) to $webOutputDir" "Success"
    }
    else {
        Write-ColorText "⚠️ Output directory not found: $outputDir" "Warning"
    }
}
else {
    Write-ColorText "📁 Skipping copy of output/ to web/output/ (NoCopy option enabled)" "Info"
}

Write-Host ""

# Step 2: Generate all dashboards (now that assets are in place)
# Run each script
Write-Section "Generating Dashboards"
$overallStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
Write-Host ""  # Add some spacing for cleaner output

# Now run all scripts
for ($i = 0; $i -lt $scripts.Count; $i++) {
    $script = $scripts[$i]
    
    # Extract just the script name without arguments for path checking
    $scriptName = ($script.Path -split ' ', 2)[0]
    
    if (Test-Path $scriptName) {
        $success = Invoke-PythonScript -ScriptPath $script.Path -Description $script.Description -StepNumber ($i + 1) -TotalSteps $totalScripts
        
        if ($success) {
            $successCount++
        }
        else {
            $failedScripts += $script
        }
    }
    else {
        Write-Host "[$($i + 1)/$totalScripts] " -NoNewline -ForegroundColor $Colors.Info
        Write-Host "Processing: " -NoNewline -ForegroundColor $Colors.Info
        Write-Host $script.Description -NoNewline -ForegroundColor $Colors.Emphasis
        Write-Host " ... " -NoNewline -ForegroundColor $Colors.Info
        Write-Host "⚠️  SKIPPED (script not found)" -ForegroundColor $Colors.Warning
        $failedScripts += $script
    }
}

$overallStopwatch.Stop()
$totalDuration = $overallStopwatch.Elapsed.TotalSeconds

# Step 3: Run PowerShell scripts for post-processing
if ($powershellScripts.Count -gt 0) {
    Write-Host ""
    Write-Section "Post-Processing with PowerShell Scripts"
    Write-Host ""
    
    for ($i = 0; $i -lt $powershellScripts.Count; $i++) {
        $psScript = $powershellScripts[$i]
        $stepNumber = $scripts.Count + $i + 1
        $totalWithPS = $scripts.Count + $powershellScripts.Count
        
        Write-Host "[$stepNumber/$totalWithPS] " -NoNewline -ForegroundColor $Colors.Info
        Write-Host "Processing: " -NoNewline -ForegroundColor $Colors.Info
        Write-Host $psScript.Description -NoNewline -ForegroundColor $Colors.Emphasis
        Write-Host " ... " -NoNewline -ForegroundColor $Colors.Info
        
        if (Test-Path $psScript.Path) {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            
            try {
                # Execute PowerShell script
                $result = & PowerShell -ExecutionPolicy Bypass -File $psScript.Path 2>&1
                $exitCode = $LASTEXITCODE
                
                $stopwatch.Stop()
                $duration = $stopwatch.Elapsed.TotalSeconds
                
                if ($exitCode -eq 0) {
                    Write-Host "✅ " -NoNewline -ForegroundColor $Colors.Success
                    Write-Host "($([math]::Round($duration, 2))s)" -ForegroundColor $Colors.Info
                    $successCount++
                }
                else {
                    Write-Host "❌ " -ForegroundColor $Colors.Error
                    Write-Host "    ERROR: $($psScript.Description) failed" -ForegroundColor $Colors.Error
                    if ($result) {
                        $truncatedResult = if ($result.Length -gt 500) { $result.Substring(0, 500) + "..." } else { $result }
                        Write-Host "    Output: $truncatedResult" -ForegroundColor $Colors.Warning
                    }
                    $failedScripts += $psScript
                }
            }
            catch {
                $stopwatch.Stop()
                Write-Host "❌ " -ForegroundColor $Colors.Error
                Write-Host "    EXCEPTION: $($_.Exception.Message)" -ForegroundColor $Colors.Error
                $failedScripts += $psScript
            }
        }
        else {
            Write-Host "⚠️  SKIPPED (script not found)" -ForegroundColor $Colors.Warning
            $failedScripts += $psScript
        }
    }
    
    # Update total scripts count for final summary
    $totalScripts = $scripts.Count + $powershellScripts.Count
}

# Clean up any old-style CSS files that might have been generated
Write-Host ""
Write-Host "🧹 " -NoNewline -ForegroundColor $Colors.Info
Write-Host "Cleaning up old CSS files..." -NoNewline -ForegroundColor $Colors.Info
Get-ChildItem -Path "$webDir\portfolio_*.css" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Force
    Write-Host " ✓" -NoNewline -ForegroundColor $Colors.Success
}
Write-Host " done" -ForegroundColor $Colors.Success

# Final step: Ensure CSS files are accessible and properly formatted
Write-Host "🎨 " -NoNewline -ForegroundColor $Colors.Info
Write-Host "Verifying CSS accessibility..." -NoNewline -ForegroundColor $Colors.Info
$cssPath = Join-Path $webDir "assets\dashboard_common.css"
if (Test-Path $cssPath) {
    $cssContent = Get-Content $cssPath -Raw
    if ($cssContent -and $cssContent.Length -gt 100) {
        Write-Host " ✅" -ForegroundColor $Colors.Success
    }
    else {
        Write-Host " ⚠️ CSS file seems incomplete" -ForegroundColor $Colors.Warning
    }
}
else {
    Write-Host " ❌ CSS file not found" -ForegroundColor $Colors.Error
}

Write-Host ""

# Generate summary
Write-Section "Generation Summary"

Write-Host "📊 " -NoNewline -ForegroundColor $Colors.Info
Write-Host "Total dashboards processed: " -NoNewline -ForegroundColor $Colors.Info
Write-Host $totalScripts -ForegroundColor $Colors.Emphasis

Write-Host "✅ " -NoNewline -ForegroundColor $Colors.Success
Write-Host "Successfully generated: " -NoNewline -ForegroundColor $Colors.Info
Write-Host $successCount -ForegroundColor $Colors.Success

Write-Host "❌ " -NoNewline -ForegroundColor $Colors.Error
Write-Host "Failed: " -NoNewline -ForegroundColor $Colors.Info
Write-Host ($totalScripts - $successCount) -ForegroundColor $Colors.Error

Write-Host "⏱️  " -NoNewline -ForegroundColor $Colors.Info
Write-Host "Total time: " -NoNewline -ForegroundColor $Colors.Info
Write-Host "$([math]::Round($totalDuration, 2)) seconds" -ForegroundColor $Colors.Emphasis

Write-Host ""

if ($successCount -eq $totalScripts) {
    Write-ColorText "🎉 ALL DASHBOARDS GENERATED SUCCESSFULLY!" "Success"
    
    Write-Host ""
    Write-ColorText "📁 Available dashboards:" "Info"
    
    $dashboards = Get-DashboardFiles
    foreach ($dashboard in $dashboards) {
        if (Test-Path $dashboard.File) {
            $fileInfo = Get-Item $dashboard.File
            $size = [math]::Round($fileInfo.Length / 1KB, 1)
            Write-Host "   • " -NoNewline -ForegroundColor $Colors.Success
            Write-Host "$($dashboard.Name): " -NoNewline -ForegroundColor $Colors.Info
            Write-Host "$($dashboard.File) " -NoNewline -ForegroundColor $Colors.Emphasis
            Write-Host "($size KB)" -ForegroundColor $Colors.Info
        }
    }
    
    Write-Host ""
    Write-ColorText "💡 CSS Information:" "Info"
    Write-Host "   • CSS is now embedded directly in HTML files for maximum compatibility" -ForegroundColor $Colors.Info
    Write-Host "   • No external CSS files needed - dashboards should display properly in any browser" -ForegroundColor $Colors.Info
    Write-Host "   • If styling issues persist, try refreshing (Ctrl+F5) or using a different browser" -ForegroundColor $Colors.Info
}
else {
    Write-ColorText "⚠️  Some dashboards failed to generate:" "Warning"
    foreach ($failed in $failedScripts) {
        Write-Host "   • " -NoNewline -ForegroundColor $Colors.Error
        Write-Host "$($failed.Description) ($($failed.Path))" -ForegroundColor $Colors.Error
    }
}

Write-Host ""

# Define the path to the main dashboard
$webDir = Join-Path $PSScriptRoot "web"
$indexPath = Join-Path $webDir "index.html"

# Offer to open the main dashboard
if (Test-Path $indexPath) {
    if ($OpenBrowser) {
        Write-Section "Opening Dashboard"
        Write-ColorText "🌐 Opening main dashboard in default browser..." "Info"
        Write-ColorText "💡 CSS is embedded directly in HTML files for maximum compatibility." "Info"
        try {
            # Convert to absolute path and open with default browser
            $absolutePath = Resolve-Path $indexPath
            Start-Process $absolutePath.Path
            Write-ColorText "✅ Dashboard opened successfully!" "Success"
            Write-ColorText "📍 Dashboard location: $($absolutePath.Path)" "Info"
        }
        catch {
            Write-ColorText "❌ Failed to open browser: $($_.Exception.Message)" "Error"
            Write-ColorText "💡 You can manually open: $indexPath" "Info"
        }
    }
    else {
        Write-ColorText "💡 To open the dashboard, run: Start-Process '$indexPath'" "Info"
    }
}
else {
    Write-ColorText "❌ Main dashboard ($indexPath) not found!" "Error"
    Write-ColorText "💡 Please check if generate_main_page.py ran successfully." "Warning"
    Write-ColorText "💡 Make sure the 'web' directory exists." "Warning"
}

Write-Host ""
Write-Header "Dashboard Generation Complete"

if ($successCount -lt $totalScripts) {
    Write-ColorText "⚠️  Review the errors above and re-run failed scripts if needed." "Warning"
}

Write-Host ""

# Exit handling
if (-not $NoPause) {
    Write-ColorText "Press any key to exit..." "Info"
    if ($Host.UI.RawUI) {
        try {
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        catch {
            Read-Host "Press Enter to exit"
        }
    }
    else {
        Read-Host "Press Enter to exit"
    }
}

# Return appropriate exit code
if ($successCount -eq $totalScripts) {
    exit 0
}
else {
    exit 1
}
