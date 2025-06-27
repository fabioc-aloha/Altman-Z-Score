@echo off
REM Enhanced batch wrapper for PowerShell portfolio analysis with help support

REM Check for help requests
if "%~1"=="/?" goto :help
if "%~1"=="-h" goto :help
if "%~1"=="--help" goto :help
if "%~1"=="help" goto :help
if "%~1"=="" goto :help

REM Parse arguments
set PORTFOLIO=%~1
set MODE=%~2
set ACCOUNT_TYPE=%~3

REM Set defaults
if "%MODE%"=="" set MODE=balanced
if "%ACCOUNT_TYPE%"=="" set ACCOUNT_TYPE=free

REM Validate portfolio parameter
if "%PORTFOLIO%"=="my" goto :run
if "%PORTFOLIO%"=="tech" goto :run
if "%PORTFOLIO%"=="international" goto :run
if "%PORTFOLIO%"=="diversified" goto :run
if exist "%PORTFOLIO%" goto :run

echo Error: Portfolio '%PORTFOLIO%' not found
echo.
echo Available built-in portfolios: my, tech, international, diversified
echo Or provide a valid file path to a custom portfolio
echo.
echo Use 'analyze_portfolio.bat help' for more information
exit /b 1

:run
echo.
echo ================================================================
echo                Portfolio Analysis - Command Prompt Wrapper
echo ================================================================
echo Portfolio: %PORTFOLIO%
echo Mode: %MODE%
echo Account Type: %ACCOUNT_TYPE%
echo.
echo Launching PowerShell analysis...
echo.

REM Execute PowerShell script with ExecutionPolicy bypass
powershell.exe -ExecutionPolicy Bypass -File "analyze_portfolio.ps1" -Portfolio "%PORTFOLIO%" -Mode "%MODE%" -AccountType "%ACCOUNT_TYPE%"

REM Check exit code and provide feedback
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Analysis completed successfully!
    echo Check the 'output' folder for results.
) else (
    echo.
    echo Analysis failed with error code: %ERRORLEVEL%
    echo Check the error messages above for details.
)
goto :end

:help
echo.
echo ================================================================
echo           Quick Portfolio Analysis - Command Prompt Wrapper
echo ================================================================
echo.
echo DESCRIPTION:
echo   Simple Command Prompt wrapper for PowerShell portfolio analysis.
echo   Provides execution policy bypass and simplified parameter syntax.
echo.
echo USAGE:
echo   analyze_portfolio.bat ^<portfolio^> [mode] [account_type]
echo   analyze_portfolio.bat help
echo.
echo PARAMETERS:
echo   portfolio     - Portfolio name or file path (REQUIRED)
echo                  Built-in: my, tech, international, diversified
echo                  Or path to custom portfolio file
echo.
echo   mode         - Analysis mode (OPTIONAL, default: balanced)
echo                  fast      - 2 processes, quick analysis
echo                  balanced  - 4 processes, standard analysis  
echo                  intensive - 6 processes, thorough analysis
echo.
echo   account_type - FMP account type (OPTIONAL, default: free)
echo                  free     - Basic analysis, 4 quarters
echo                  enhanced - Advanced analysis, 12 quarters
echo.
echo EXAMPLES:
echo   analyze_portfolio.bat help
echo   analyze_portfolio.bat my
echo   analyze_portfolio.bat tech intensive
echo   analyze_portfolio.bat international balanced enhanced
echo   analyze_portfolio.bat "custom\my_stocks.txt" intensive enhanced
echo.
echo BUILT-IN PORTFOLIOS:
echo   my           - portfolios/my_portfolio.txt
echo   tech         - portfolios/tech_portfolio.txt
echo   international- portfolios/international_portfolio.txt
echo   diversified  - portfolios/diversified_portfolio.txt
echo.
echo MODE COMPARISON:
echo   fast      - Good for testing or small portfolios
echo   balanced  - Recommended for most use cases
echo   intensive - Best for large portfolios on powerful systems
echo.
echo ACCOUNT DIFFERENCES:
echo   free     - 4 quarters, basic indicators, standard analysis
echo   enhanced - 12 quarters, advanced indicators, AI insights
echo.
echo ADVANCED OPTIONS:
echo   For more detailed help and advanced options, use:
echo   powershell.exe -File "analyze_portfolio.ps1" -Help
echo.
echo OUTPUT:
echo   Results saved to 'output' folder with individual ticker directories
echo   Each ticker includes: charts, reports, CSV data, AI insights
echo.
goto :end

:end
