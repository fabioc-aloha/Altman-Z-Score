@echo off
REM Search for BUY ratings in all full report markdown files and save clickable file:// links to output\buy_reports.md

set "outfile=output\buy_reports.md"
echo # BUY Ratings Report > "%outfile%"
echo. >> "%outfile%"

for /f "usebackq delims=" %%F in (`powershell -Command "Select-String -Path .\output\*\zscore_*_zscore_full_report.md -Pattern 'BUY' | Select-Object -ExpandProperty Path | Get-Unique"`) do (
    echo [%%~nxF](file:///%%~fF) >> "%outfile%"
)

echo Done. Links saved to %outfile%.
echo.