![Altman Z-Score Analysis Platform](banner.png)

# Altman Z-Score Analysis Platform

**Version: 3.3.0 (2025-06-17)**

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with LLM-powered qualitative insights. This script orchestrates the analysis pipeline for single or multiple stock tickers. See [MODELS.md](MODELS.md) for available Z-Score models and selection guidelines.

---

## Architecture Overview
1. **Input Layer:** Accepts ticker(s) and analysis date; validates input.
2. **Data Fetching Layer:** Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance).
3. **Validation Layer:** Validates raw data using Pydantic schemas; reports missing/invalid fields.
4. **Computation Layer:** Computes Altman Z-Score using validated data; returns result object.
5. **Reporting Layer:** Outputs results to CSV, JSON, or stdout; logs all steps and errors.

### Key Principles
- **Modularity:** Each phase is implemented as a separate, testable module.
- **Robustness:** Strong error handling, logging, and data validation at every step.
- **Visualization:** Rich visual analytics with candlestick charts, company branding, and clear data representation.
- **Error Handling:** Graceful continuation for multi-ticker analysis and informative error messages.
- **Model Selection:** Intelligent model selection based on company characteristics (see [MODELS.md](MODELS.md))

### Features
- Multiple Z-Score models for different company types and industries
- Company-branded visualization with logos and professional charts
- Candlestick representation for weekly price trends
- Multi-ticker analysis with graceful error handling
- Comprehensive Z-Score analysis with LLM insights

### Data Sources
- **Primary:** Yahoo Finance (real-time financials and market data)
- **Fallback:** SEC EDGAR/XBRL (official regulatory filings)
- **Executive Data:** Multi-source aggregation for comprehensive profiles

### Output Structure
All outputs are saved to `output/<TICKER>/`:
- `zscore_<TICKER>_zscore_full_report.md` (comprehensive analysis with LLM insights)
- `zscore_<TICKER>_trend.png` (trend visualization chart)
- `zscore_<TICKER>.csv` and `.json` (raw analytical data)
- `<TICKER>_NOT_AVAILABLE.txt` (marker for unavailable tickers)

---

## Usage
To analyze one or more stocks, run:
```sh
python main.py <TICKER1> <TICKER2> ... [--start YYYY-MM-DD] [--no-plot] [--test] [--log-level DEBUG]
```

Examples:
```sh
python main.py AAPL MSFT TSLA
python main.py TSLA --start 2023-01-01
python main.py AAPL MSFT --no-plot
python main.py --test
python main.py --log-level DEBUG
```
Replace `<TICKER1> <TICKER2> ...` with one or more stock ticker symbols (e.g., `AAPL`, `MSFT`).

---

## Sample Reports

The following table shows available reports for all analyzed tickers:

<!-- BEGIN_TICKERS_TABLE -->
| Logo | Company Name | Full Report | Trend Chart |
|------|-------------|-------------|:-------------:|
| <img src="output/AAPL/AAPL_logo.png" alt="AAPL" width="80" height="80"/> | Apple Inc | [Report](output/AAPL/zscore_AAPL_zscore_full_report.md) | <a href="output/AAPL/zscore_AAPL_trend.png"><img src="output/AAPL/zscore_AAPL_trend.png" alt="AAPL Chart" width="400"/></a> |
| <img src="output/AMZN/AMZN_logo.png" alt="AMZN" width="80" height="80"/> | Amazon.com Inc | [Report](output/AMZN/zscore_AMZN_zscore_full_report.md) | <a href="output/AMZN/zscore_AMZN_trend.png"><img src="output/AMZN/zscore_AMZN_trend.png" alt="AMZN Chart" width="400"/></a> |
| <img src="output/GOOGL/GOOGL_logo.png" alt="GOOGL" width="80" height="80"/> | Alphabet Inc | [Report](output/GOOGL/zscore_GOOGL_zscore_full_report.md) | <a href="output/GOOGL/zscore_GOOGL_trend.png"><img src="output/GOOGL/zscore_GOOGL_trend.png" alt="GOOGL Chart" width="400"/></a> |
| <img src="output/MSFT/MSFT_logo.png" alt="MSFT" width="80" height="80"/> | Microsoft Corp | [Report](output/MSFT/zscore_MSFT_zscore_full_report.md) | <a href="output/MSFT/zscore_MSFT_trend.png"><img src="output/MSFT/zscore_MSFT_trend.png" alt="MSFT Chart" width="400"/></a> |
| <img src="output/NVDA/NVDA_logo.png" alt="NVDA" width="80" height="80"/> | NVIDIA Corp | [Report](output/NVDA/zscore_NVDA_zscore_full_report.md) | <a href="output/NVDA/zscore_NVDA_trend.png"><img src="output/NVDA/zscore_NVDA_trend.png" alt="NVDA Chart" width="400"/></a> |
| <img src="output/PG/PG_logo.png" alt="PG" width="80" height="80"/> | Procter & Gamble Co | [Report](output/PG/zscore_PG_zscore_full_report.md) | <a href="output/PG/zscore_PG_trend.png"><img src="output/PG/zscore_PG_trend.png" alt="PG Chart" width="400"/></a> |
| <img src="output/TSLA/TSLA_logo.png" alt="TSLA" width="80" height="80"/> | Tesla Inc | [Report](output/TSLA/zscore_TSLA_zscore_full_report.md) | <a href="output/TSLA/zscore_TSLA_trend.png"><img src="output/TSLA/zscore_TSLA_trend.png" alt="TSLA Chart" width="400"/></a> |
| <img src="output/UNH/UNH_logo.png" alt="UNH" width="80" height="80"/> | UnitedHealth Group Inc | [Report](output/UNH/zscore_UNH_zscore_full_report.md) | <a href="output/UNH/zscore_UNH_trend.png"><img src="output/UNH/zscore_UNH_trend.png" alt="UNH Chart" width="400"/></a> |
| <img src="output/WMT/WMT_logo.png" alt="WMT" width="80" height="80"/> | Walmart Inc | [Report](output/WMT/zscore_WMT_zscore_full_report.md) | <a href="output/WMT/zscore_WMT_trend.png"><img src="output/WMT/zscore_WMT_trend.png" alt="WMT Chart" width="400"/></a> |
<!-- END_TICKERS_TABLE -->

---

## Updating the Sample Reports Table

To automatically update the sample reports table in this README, use the provided script:

- **`generate_readme_table.py`**: Scans the `output/` directory for tickers with all required report files and automatically updates the table section in the README.md file (between the markers).

Usage:
```sh
python generate_readme_table.py
```

The script:
1. Generates the table and saves it to `table.md`
2. Automatically updates the table in README.md between the `<!-- BEGIN_TICKERS_TABLE -->` and `<!-- END_TICKERS_TABLE -->` markers
3. Shows a confirmation message when the update is successful

---

## Recent Improvements (3.0.0) ✅ FULLY COMPLETED
- **✅ Full modular reorganization:** All code grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- **✅ All imports fixed:** Updated to use new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`)
- **✅ Integration testing:** Added `tests/test_integration_main.py` to catch import/runtime errors in main pipeline
- **✅ Critical import fixes:** Resolved all ModuleNotFoundError issues across the codebase (fetcher_factory.py, industry_classifier.py, etc.)
- **✅ Main pipeline verified:** Successfully runs `python main.py msft` without import errors
- **✅ Improved LLM prompt templates:** Enhanced code injection for reporting with more complete, context-aware, and robust analysis outputs
- **✅ Documentation updated:** All documentation reflects new structure and completed modularization
- **✅ All tests passing:** Both unit tests and integration tests pass after reorganization
- **✅ Modularization & refactoring complete:** All refactoring work finished and fully tested

**🎯 v3.0.0 is now ready for production deployment and user feedback collection.**

---

## Documentation & Project Roadmap
- For the unified project plan, roadmap, actionable tasks, and technical references, see [TODO.md](./TODO.md)
- See `LEARNINGS.md` for technical notes and known issues
- **For LLM Copilot troubleshooting and analysis:** See [copilot.md](./copilot.md) for step-by-step instructions on analyzing pipeline outputs and debugging issues using VS Code tools

---

## Environment Setup
- Copy `.env.example` to `.env` and fill in your API keys and configuration
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Use Python 3.11+ (see virtual environment setup instructions below)

---

## Development & Contribution
- All changes must pass existing and new tests
- New features require updated tests and documentation
- Document significant learnings in `LEARNINGS.md`

## Troubleshooting & Analysis Tools

### LLM Copilot Analysis
The repository includes `copilot.md` - comprehensive instructions for LLM Copilot to systematically analyze pipeline outputs, identify issues, and troubleshoot problems using VS Code tools.

**Key Features:**
- **Automated Analysis:** Step-by-step instructions using VS Code tools (list_dir, read_file, grep_search, etc.)
- **Success Rate Assessment:** Comprehensive evaluation of ticker analysis completeness
- **Issue Pattern Detection:** Systematic identification of common failure modes
- **Root Cause Analysis:** Detailed investigation workflows for debugging
- **Solution Documentation:** Required logging of all findings before code changes

**Usage for LLM Copilot:**
1. Follow the workflow in `copilot.md` to analyze all processed tickers
2. Create detailed troubleshooting logs in `Copilot_Troubleshoot.md`
3. Identify and prioritize the most common issues
4. Develop and test solutions based on documented findings

**Human Usage:**
The same systematic approach can be followed manually for pipeline analysis and debugging.

### Quick Start for Issue Analysis
```bash
# Analyze current pipeline outputs
python -c "
import os
print('Available tickers in output/:')
for ticker in os.listdir('output'):
    print(f'  {ticker}')
"

# Test a specific ticker with debug logging
python main.py MSFT --start 2024-01-01 --log-level DEBUG
```

---

## License
MIT (see LICENSE file)

---

## Data/API Credits & Disclaimers

This project uses data and APIs from the following sources:
- **Yahoo Finance** (yfinance): Market data and financials. Not affiliated with or endorsed by Yahoo. Data may be delayed or incomplete. See Yahoo's terms of use.
- **Finnhub.io**: Company profiles, logos, and additional financial data. Not affiliated with or endorsed by Finnhub. Data provided under Finnhub's free and paid API terms.
- **SEC EDGAR/XBRL**: Official regulatory filings. Data is public domain but may be subject to update delays or errors.

**Disclaimers:**
- All trademarks, service marks, and company names are the property of their respective owners.
- This project is not affiliated with, endorsed by, or sponsored by Yahoo, Finnhub, the SEC, or any other data provider.
- Data is provided "as is" for informational and educational purposes only. No warranty is made as to accuracy, completeness, or timeliness. Use at your own risk.
- Always consult the official data provider's terms of service and licensing before commercial use.

---

For more details, see the full documentation in this repository and referenced files.

## Project Structure (as of 3.0.0)

```
src/altman_zscore/
    api/                # API clients and integrations (Finnhub, OpenAI, SEC, Yahoo, etc.)
    company/            # Company profile, status, helpers, CIK/SIC lookup
    computation/        # Z-Score computation, constants, formulas, DRY helpers
    core/               # Main pipeline, orchestration, progress tracking, reporting
    data_fetching/      # Financial and market data fetching (Yahoo, SEC, etc.)
    market/             # Market data helpers and utilities
    misc/               # Shared utilities and miscellaneous helpers
    models/             # Z-Score models, thresholds, enums, industry classifier
    plotting/           # Visualization, plotting helpers, terminal output
    schemas/            # Pydantic schemas and data validation models
    utils/              # Paths, IO, logging, error handling, etc.
    validation/         # Data validation logic
    prompts/            # LLM prompt templates
    ...
output/                 # Analysis results, reports, and plots (per ticker)
tests/                  # Unit and integration tests
```

- Each folder contains focused, testable modules.
- All imports use the new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`).
- For the project plan, roadmap, and actionable tasks, see [TODO.md](./TODO.md)

---

## Example: Plotting Z-Score Trend

To generate a Z-Score trend plot in your own script or notebook:

```python
from altman_zscore.plotting.plotting_main import plot_zscore_trend

# df: DataFrame with columns ['quarter_end', 'zscore']
# ticker: str, model: str, out_base: str
plot_zscore_trend(df, ticker, model, out_base)
```
