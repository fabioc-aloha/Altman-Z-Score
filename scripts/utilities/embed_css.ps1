# ===============================================================================
# CSS Embedding Utility for Altman Z-Score Dashboards
# This PowerShell script embeds CSS directly into HTML files
# ===============================================================================

param(
    [string]$WebDirectory = "web",
    [string]$CssFile = "assets\dashboard_common.css",
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "Info"
    )
    
    $color = switch ($Status) {
        "Success" { "Green" }
        "Error" { "Red" }
        "Warning" { "Yellow" }
        default { "White" }
    }
    
    Write-Host $Message -ForegroundColor $color
}

function Embed-CSSIntoHTML {
    param(
        [string]$HtmlFilePath,
        [string]$CssContent
    )
    
    if (-not (Test-Path $HtmlFilePath)) {
        Write-Status "HTML file not found: $HtmlFilePath" "Error"
        return $false
    }
    
    try {
        # Read the HTML content
        $htmlContent = Get-Content $HtmlFilePath -Raw -Encoding UTF8
        
        # Check if CSS is already embedded
        if ($htmlContent -match '<style>[\s\S]*?</style>') {
            if ($Verbose) {
                Write-Status "CSS already embedded in: $(Split-Path $HtmlFilePath -Leaf)" "Warning"
            }
            return $true
        }
        
        # Check if there's a CSS link to replace
        $cssLinkPattern = '<link[^>]*\.css[^>]*>'
        
        if ($htmlContent -match $cssLinkPattern) {
            # Replace the CSS link with embedded CSS
            $embeddedCss = "<style>`n$CssContent`n</style>"
            $htmlContent = $htmlContent -replace $cssLinkPattern, $embeddedCss
        }
        else {
            # Insert CSS into the head section
            $embeddedCss = "<style>`n$CssContent`n</style>"
            
            if ($htmlContent -match '</head>') {
                $htmlContent = $htmlContent -replace '</head>', "$embeddedCss`n</head>"
            }
            elseif ($htmlContent -match '<head>') {
                $htmlContent = $htmlContent -replace '<head>', "<head>`n$embeddedCss"
            }
            else {
                # If no head tag, insert after <html> or at the beginning
                if ($htmlContent -match '<html[^>]*>') {
                    $htmlContent = $htmlContent -replace '(<html[^>]*>)', "`$1`n<head>`n$embeddedCss`n</head>"
                }
                else {
                    $htmlContent = "$embeddedCss`n$htmlContent"
                }
            }
        }
        
        # Write the modified content back to the file
        Set-Content -Path $HtmlFilePath -Value $htmlContent -Encoding UTF8
        
        return $true
    }
    catch {
        Write-Status "Error processing $HtmlFilePath`: $($_.Exception.Message)" "Error"
        return $false
    }
}

# Main execution
Write-Status "🎨 Starting CSS Embedding Process..." "Info"

# Resolve paths
$webPath = Join-Path $PSScriptRoot $WebDirectory
$cssPath = Join-Path $webPath $CssFile

Write-Status "📁 Web directory: $webPath" "Info"
Write-Status "🎨 CSS file: $cssPath" "Info"

# Check if directories exist
if (-not (Test-Path $webPath)) {
    Write-Status "Web directory not found: $webPath" "Error"
    exit 1
}

if (-not (Test-Path $cssPath)) {
    Write-Status "CSS file not found: $cssPath" "Error"
    exit 1
}

# Read the CSS content
try {
    $cssContent = Get-Content $cssPath -Raw -Encoding UTF8
    $cssSize = ([System.Text.Encoding]::UTF8.GetBytes($cssContent)).Length
    $message = "Successfully loaded CSS file ($cssSize characters)"
    Write-Status $message "Success"
}
catch {
    Write-Status "Failed to read CSS file: $($_.Exception.Message)" "Error"
    exit 1
}

# Find all HTML files in the web directory
$htmlFiles = Get-ChildItem -Path $webPath -Filter "*.html" -File

if ($htmlFiles.Count -eq 0) {
    Write-Status "No HTML files found in: $webPath" "Warning"
    exit 0
}

Write-Status "📄 Found $($htmlFiles.Count) HTML files to process" "Info"
Write-Host ""

# Process each HTML file
$successCount = 0
$skipCount = 0
$errorCount = 0

foreach ($htmlFile in $htmlFiles) {
    $fileName = $htmlFile.Name
    Write-Host "Processing: " -NoNewline
    Write-Host $fileName -ForegroundColor Cyan -NoNewline
    Write-Host " ... " -NoNewline
    
    $success = Embed-CSSIntoHTML -HtmlFilePath $htmlFile.FullName -CssContent $cssContent
    
    if ($success) {
        # Check if CSS was actually embedded (not skipped)
        $htmlContent = Get-Content $htmlFile.FullName -Raw
        if ($htmlContent -match '<style>[\s\S]*?</style>') {
            Write-Host "✅ Embedded" -ForegroundColor Green
            $successCount++
        }
        else {
            Write-Host "⚠️ Skipped" -ForegroundColor Yellow
            $skipCount++
        }
    }
    else {
        Write-Host "❌ Failed" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Status "📊 Processing Summary:" "Info"
Write-Status "   ✅ Successfully processed: $successCount files" "Success"
Write-Status "   ⚠️ Skipped (already embedded): $skipCount files" "Warning"
Write-Status "   ❌ Failed: $errorCount files" $(if ($errorCount -gt 0) { "Error" } else { "Info" })

if ($successCount -gt 0) {
    Write-Host ""
    Write-Status "🎉 CSS embedding completed successfully!" "Success"
    Write-Status "💡 All HTML files now have embedded CSS and should display properly when opened directly in a browser." "Info"
    
    # Clean up - remove external CSS links that are no longer needed
    $assetsDir = Join-Path $webPath "assets"
    if (Test-Path $assetsDir) {
        Write-Host ""
        Write-Status "🧹 Note: You can now optionally remove the external CSS files from the assets directory if desired." "Info"
        Write-Status "   External CSS files are no longer needed since CSS is now embedded in HTML files." "Info"
    }
}

if ($errorCount -gt 0) {
    Write-Status "⚠️ Some files had errors. Please check the output above for details." "Warning"
    exit 1
}

exit 0
