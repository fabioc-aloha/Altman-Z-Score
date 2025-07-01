@echo off
REM ===============================================================================
REM RETAIL Z-SCORE MODEL VALIDATION - BATCH SCRIPT
REM Quick validation runner for the novel retail Z-Score model
REM ===============================================================================

echo.
echo ===============================================================================
echo RETAIL Z-SCORE MODEL VALIDATION
echo Novel Retail-Specific Bankruptcy Prediction Model Testing  
echo ===============================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ and add to PATH.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "altman_zscore" (
    echo ERROR: altman_zscore module not found. Please run from project root directory.
    pause
    exit /b 1
)

REM Check if portfolio file exists
if not exist "portfolios\retail_backtest_portfolio.txt" (
    echo ERROR: Retail backtest portfolio file not found.
    pause
    exit /b 1
)

echo Prerequisites check: PASSED
echo.

echo RETAIL BACKTEST PORTFOLIO SUMMARY:
echo   - Failed/Bankrupt Retailers: 20 companies
echo   - Retailers in Distress: 15 companies  
echo   - Recovery/Turnaround Stories: 10 companies
echo   - Stable/Strong Retailers: 15 companies
echo   - Seasonal/Cyclical Retailers: 15 companies
echo   TOTAL: 75 companies
echo.

echo VALIDATION OPTIONS:
echo   1. Quick Test (10 representative companies, ~15 minutes)
echo   2. Full Validation (75 companies, ~2-3 hours)
echo   3. Model Comparison (retail vs traditional models)
echo   4. Exit
echo.

set /p choice="Select option (1-4): "

if "%choice%"=="1" goto :quicktest
if "%choice%"=="2" goto :fullvalidation
if "%choice%"=="3" goto :comparison
if "%choice%"=="4" goto :exit
echo Invalid choice. Please select 1-4.
pause
goto :end

:quicktest
echo.
echo STARTING QUICK TEST...
echo Creating subset portfolio for development testing...

REM Create quick test portfolio
(
echo # Quick Test Portfolio - Representative Retail Companies
echo # Failed Retailers
echo TOY
echo SHLDQ
echo JCPNQ
echo # Distressed Retailers
echo BBBY
echo GME
echo M
echo # Stable Retailers  
echo AMZN
echo COST
echo HD
echo # Seasonal Retailers
echo SPIR
echo TSCO
) > portfolios\retail_quick_test.txt

echo Running validation...
python validate_retail_model.py --portfolio portfolios\retail_quick_test.txt --output-dir backtest_results\quick_test --comparison

if errorlevel 1 (
    echo ERROR: Quick test failed.
    pause
    goto :end
)

echo.
echo ✓ Quick test completed successfully!
echo Results saved to: backtest_results\quick_test\
goto :showresults

:fullvalidation
echo.
echo STARTING FULL VALIDATION...
echo This comprehensive analysis will take 2-3 hours...
echo Processing 75 retail companies across all categories...

python validate_retail_model.py --portfolio portfolios\retail_backtest_portfolio.txt --output-dir backtest_results --comparison --detailed

if errorlevel 1 (
    echo ERROR: Full validation failed.
    pause
    goto :end
)

echo.
echo ✓ Full validation completed successfully!
echo Results saved to: backtest_results\
goto :showresults

:comparison
echo.
echo STARTING MODEL COMPARISON...
echo Comparing retail model vs traditional Z-Score models...

echo Step 1: Analyzing with retail model...
python main.py --portfolio portfolios\retail_backtest_portfolio.txt --model retail --output backtest_results\retail_results

echo Step 2: Analyzing with original model...  
python main.py --portfolio portfolios\retail_backtest_portfolio.txt --model original --output backtest_results\original_results

echo Step 3: Generating comparative analysis...
python validate_retail_model.py --portfolio portfolios\retail_backtest_portfolio.txt --output-dir backtest_results --comparison

if errorlevel 1 (
    echo ERROR: Model comparison failed.
    pause
    goto :end
)

echo.
echo ✓ Model comparison completed successfully!
echo Results saved to: backtest_results\
goto :showresults

:showresults
echo.
echo ===============================================================================
echo VALIDATION RESULTS
echo ===============================================================================

if exist "backtest_results\validation_report.md" (
    echo ✓ Validation Report: backtest_results\validation_report.md
)

if exist "backtest_results\raw_results.json" (
    echo ✓ Raw Results: backtest_results\raw_results.json
)

echo.
echo NEXT STEPS:
echo   1. Review validation report for detailed analysis
echo   2. Check bankruptcy prediction accuracy vs targets
echo   3. Analyze inventory component effectiveness  
echo   4. Consider model refinements based on results
echo   5. Use results for academic publication preparation
echo.

echo Opening results directory...
start backtest_results

:exit
echo.
echo Validation complete. Thank you for testing the retail Z-Score model!
echo.
echo For detailed usage instructions, see:
echo   - NOVEL_RETAIL_MODEL.md (Academic paper)
echo   - run_retail_validation.ps1 (PowerShell script with more options)
echo   - validate_retail_model.py (Python validation framework)

:end
pause
