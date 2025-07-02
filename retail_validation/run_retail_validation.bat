@echo off
REM ===============================================================================
REM Retail Z-Score Model Validation - Windows Batch Launcher
REM ===============================================================================

echo.
echo ===============================================================================
echo RETAIL Z-SCORE MODEL VALIDATION LAUNCHER
echo ===============================================================================
echo.
echo This batch file provides easy access to the retail validation framework.
echo.
echo Available Options:
echo   1. Quick Test (11 companies, ~15-30 minutes)
echo   2. Full Validation (42 companies, ~2-3 hours)
echo   3. Show Configuration
echo   4. Help
echo   5. Exit
echo.

:MENU
set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting Quick Test...
    powershell -ExecutionPolicy Bypass -File "retail_validation\scripts\run_retail_validation.ps1" -QuickTest
    goto END
)

if "%choice%"=="2" (
    echo.
    echo Starting Full Validation...
    echo This will take 2-3 hours. Are you sure? ^(Y/N^)
    set /p confirm=""
    if /i "%confirm%"=="Y" (
        powershell -ExecutionPolicy Bypass -File "retail_validation\scripts\run_retail_validation.ps1" -FullValidation
    ) else (
        echo Full validation cancelled.
    )
    goto END
)

if "%choice%"=="3" (
    echo.
    echo Showing Validation Configuration...
    powershell -ExecutionPolicy Bypass -File "retail_validation\scripts\run_retail_validation.ps1" -ShowConfig
    goto END
)

if "%choice%"=="4" (
    echo.
    echo Showing Help...
    powershell -ExecutionPolicy Bypass -File "retail_validation\scripts\run_retail_validation.ps1" -Help
    goto END
)

if "%choice%"=="5" (
    goto END
)

echo Invalid choice. Please select 1-5.
goto MENU

:END
echo.
echo Press any key to exit...
pause >nul
