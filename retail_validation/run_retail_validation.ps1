# ===============================================================================
# Retail Z-Score Model Validation - PowerShell Launcher
# ===============================================================================

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host "RETAIL Z-SCORE MODEL VALIDATION LAUNCHER" -ForegroundColor Yellow
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This script provides easy access to the retail validation framework." -ForegroundColor White
    Write-Host ""
    Write-Host "Available Options:" -ForegroundColor White
    Write-Host "  1. Quick Test (12 companies, ~7-10 minutes)" -ForegroundColor Green
    Write-Host "  2. Full Validation (54 companies, ~2-3 hours)" -ForegroundColor Yellow
    Write-Host "  3. Show Configuration" -ForegroundColor Cyan
    Write-Host "  4. Help" -ForegroundColor Magenta
    Write-Host "  5. Exit" -ForegroundColor Red
    Write-Host ""
}

function Get-UserChoice {
    do {
        $choice = Read-Host "Select option (1-5)"
        if ($choice -match '^[1-5]$') {
            return $choice
        }
        Write-Host "Invalid choice. Please select 1-5." -ForegroundColor Red
    } while ($true)
}

function Confirm-FullValidation {
    Write-Host ""
    Write-Host "Starting Full Validation..." -ForegroundColor Yellow
    Write-Host "This will take 2-3 hours and analyze 54 companies." -ForegroundColor Yellow
    Write-Host ""
    
    do {
        $confirm = Read-Host "Are you sure you want to continue? (Y/N)"
        if ($confirm -match '^[Yy]$') {
            return $true
        }
        elseif ($confirm -match '^[Nn]$') {
            return $false
        }
        Write-Host "Please enter Y for Yes or N for No." -ForegroundColor Red
    } while ($true)
}

function Main {
    try {
        do {
            Show-Menu
            $choice = Get-UserChoice
            
            switch ($choice) {
                "1" {
                    Write-Host ""
                    Write-Host "Starting Quick Test..." -ForegroundColor Green
                    Push-Location ".."
                    try {
                        & "retail_validation\scripts\run_retail_validation.ps1" -QuickTest
                    }
                    finally {
                        Pop-Location
                    }
                    break
                }
                "2" {
                    if (Confirm-FullValidation) {
                        Write-Host ""
                        Write-Host "Starting full validation..." -ForegroundColor Green
                        Push-Location ".."
                        try {
                            & "retail_validation\scripts\run_retail_validation.ps1" -FullValidation
                        }
                        finally {
                            Pop-Location
                        }
                    }
                    else {
                        Write-Host "Full validation cancelled." -ForegroundColor Yellow
                    }
                    break
                }
                "3" {
                    Write-Host ""
                    Write-Host "Showing Validation Configuration..." -ForegroundColor Cyan
                    Push-Location ".."
                    try {
                        & "retail_validation\scripts\run_retail_validation.ps1" -ShowConfig
                    }
                    finally {
                        Pop-Location
                    }
                    break
                }
                "4" {
                    Write-Host ""
                    Write-Host "Showing Help..." -ForegroundColor Magenta
                    Push-Location ".."
                    try {
                        & "retail_validation\scripts\run_retail_validation.ps1" -Help
                    }
                    finally {
                        Pop-Location
                    }
                    break
                }
                "5" {
                    Write-Host ""
                    Write-Host "Goodbye!" -ForegroundColor Green
                    return
                }
            }
            
            if ($choice -ne "5") {
                Write-Host ""
                Write-Host "Press any key to return to menu..." -ForegroundColor Gray
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            
        } while ($choice -ne "5")
    }
    catch {
        Write-Host "An error occurred: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Run the main function
Main
