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

.EXAMPLE
    .\generate_all_dashboards.ps1
    Generates all dashboards and opens the main page in browser.

.EXAMPLE
    .\generate_all_dashboards.ps1 -Verbose -NoPause
    Generates dashboards with detailed output and exits immediately.

.EXAMPLE
    .\generate_all_dashboards.ps1 -OpenBrowser:$false
    Generates dashboards without opening browser.
#>

#Requires -Version 5.1

param(
    [switch]$OpenBrowser,
    [switch]$Verbose,
    [switch]$NoPause
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
    Write-Host "=" * 80 -ForegroundColor $Colors.Header
    Write-Host (" " * ((80 - $Title.Length) / 2)) + $Title -ForegroundColor $Colors.Header
    Write-Host "=" * 80 -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    
    Write-Host ""
    Write-Host "-" * 80 -ForegroundColor $Colors.Info
    Write-Host $Title -ForegroundColor $Colors.Emphasis
    Write-Host "-" * 80 -ForegroundColor $Colors.Info
}

function Invoke-PythonScript {
    param(
        [string]$ScriptPath,
        [string]$Description,
        [int]$StepNumber,
        [int]$TotalSteps
    )
    
    Write-Host "[$StepNumber/$TotalSteps] " -NoNewline -ForegroundColor $Colors.Info
    Write-Host "Running: " -NoNewline -ForegroundColor $Colors.Info
    Write-Host $ScriptPath -ForegroundColor $Colors.Emphasis
    
    if ($Verbose) {
        Write-Host "    Description: $Description" -ForegroundColor $Colors.Info
    }
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    try {
        $result = & $script:PythonCommand $ScriptPath 2>&1
        $exitCode = $LASTEXITCODE
        
        $stopwatch.Stop()
        $duration = $stopwatch.Elapsed.TotalSeconds
        
        if ($exitCode -eq 0) {
            Write-Host "    ✅ SUCCESS: " -NoNewline -ForegroundColor $Colors.Success
            Write-Host "$Description generated successfully " -NoNewline -ForegroundColor $Colors.Success
            Write-Host "($([math]::Round($duration, 2))s)" -ForegroundColor $Colors.Info
            return $true
        }
        else {
            Write-Host "    ❌ ERROR: " -NoNewline -ForegroundColor $Colors.Error
            Write-Host "Failed to generate $Description" -ForegroundColor $Colors.Error
            if ($Verbose -and $result) {
                Write-Host "    Output: $result" -ForegroundColor $Colors.Warning
            }
            return $false
        }
    }
    catch {
        $stopwatch.Stop()
        Write-Host "    ❌ EXCEPTION: " -NoNewline -ForegroundColor $Colors.Error
        Write-Host $_.Exception.Message -ForegroundColor $Colors.Error
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
    $dashboards = @(
        @{ File = "index.html"; Name = "Main Navigation" },
        @{ File = "strong_buys.html"; Name = "Strong Buys" },
        @{ File = "conservative_picks.html"; Name = "Conservative Picks" },
        @{ File = "dividend_picks.html"; Name = "Dividend Picks" },
        @{ File = "value_picks.html"; Name = "Value Picks" },
        @{ File = "growth_picks.html"; Name = "Growth Picks" },
        @{ File = "aggressive_picks.html"; Name = "Aggressive Picks" },
        @{ File = "sell_picks.html"; Name = "Sell Recommendations" },
        @{ File = "strong_sell_picks.html"; Name = "Strong Sell Recommendations" }
    )
    
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

# Define the scripts to run
$scripts = @(
    @{ Path = "generate_strong_buys.py"; Description = "Strong Buys Dashboard" },
    @{ Path = "generate_conservative_picks.py"; Description = "Conservative Picks Dashboard" },
    @{ Path = "generate_dividend_picks.py"; Description = "Dividend Picks Dashboard" },
    @{ Path = "generate_value_picks.py"; Description = "Value Picks Dashboard" },
    @{ Path = "generate_growth_picks.py"; Description = "Growth Picks Dashboard" },
    @{ Path = "generate_aggressive_picks.py"; Description = "Aggressive Picks Dashboard" },
    @{ Path = "generate_sell_picks.py"; Description = "Sell Recommendations Dashboard" },
    @{ Path = "generate_strong_sell_picks.py"; Description = "Strong Sell Recommendations Dashboard" },
    @{ Path = "generate_main_page.py"; Description = "Main Navigation Page" }
)

# Initialize counters
$totalScripts = $scripts.Count
$successCount = 0
$failedScripts = @()

# Run each script
Write-Section "Generating Dashboards"
$overallStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

for ($i = 0; $i -lt $scripts.Count; $i++) {
    $script = $scripts[$i]
    
    if (Test-Path $script.Path) {
        $success = Invoke-PythonScript -ScriptPath $script.Path -Description $script.Description -StepNumber ($i + 1) -TotalSteps $totalScripts
        
        if ($success) {
            $successCount++
        }
        else {
            $failedScripts += $script
        }
    }
    else {
        Write-Host "[$($i + 1)/$totalScripts] " -NoNewline -ForegroundColor $Colors.Warning
        Write-Host "⚠️  SKIPPED: " -NoNewline -ForegroundColor $Colors.Warning
        Write-Host "$($script.Path) not found" -ForegroundColor $Colors.Warning
        $failedScripts += $script
    }
    
    Write-Host ""
}

$overallStopwatch.Stop()
$totalDuration = $overallStopwatch.Elapsed.TotalSeconds

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
}
else {
    Write-ColorText "⚠️  Some dashboards failed to generate:" "Warning"
    foreach ($failed in $failedScripts) {
        Write-Host "   • " -NoNewline -ForegroundColor $Colors.Error
        Write-Host "$($failed.Description) ($($failed.Path))" -ForegroundColor $Colors.Error
    }
}

Write-Host ""

# Offer to open the main dashboard
if (Test-Path "index.html") {
    if ($OpenBrowser) {
        Write-Section "Opening Dashboard"
        Write-ColorText "🌐 Opening main dashboard in default browser..." "Info"
        try {
            Start-Process "index.html"
            Write-ColorText "✅ Dashboard opened successfully!" "Success"
        }
        catch {
            Write-ColorText "❌ Failed to open browser: $($_.Exception.Message)" "Error"
            Write-ColorText "💡 You can manually open: index.html" "Info"
        }
    }
    else {
        Write-ColorText "💡 To open the dashboard, run: Start-Process 'index.html'" "Info"
    }
}
else {
    Write-ColorText "❌ Main dashboard (index.html) not found!" "Error"
    Write-ColorText "💡 Please check if generate_main_page.py ran successfully." "Warning"
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
        } catch {
            Read-Host "Press Enter to exit"
        }
    } else {
        Read-Host "Press Enter to exit"
    }
}

# Return appropriate exit code
if ($successCount -eq $totalScripts) {
    exit 0
} else {
    exit 1
}
