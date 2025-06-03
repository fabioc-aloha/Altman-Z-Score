# Altman Z-Score Analysis Platform

**Version: 2.7.3 (2025-06-03)**

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

**Release v2.7.3 (June 3, 2025):**
- Codebase cleanup: removed dead code, verified all modules and prompt files are referenced and in use
- Updated documentation and version numbers for v2.7.3
- No breaking changes; all outputs and APIs remain stable
- See RELEASE_CHECKLIST.md for detailed release notes

---

## Usage
To analyze one or more stocks, run:
```sh
python main.py <TICKER1> <TICKER2> ... [--start YYYY-MM-DD] [--moving-averages] [--no-plot]
```
Examples:
```sh
python main.py AAPL MSFT TSLA
python main.py TSLA --start 2023-01-01
python main.py AAPL MSFT --moving-averages --no-plot
```
Replace `<TICKER1> <TICKER2> ...` with one or more stock ticker symbols (e.g., `AAPL`, `MSFT`).

Outputs are saved in `output/<TICKER>/`:
- Full report: `zscore_<TICKER>_zscore_full_report.md`
- Trend chart: `zscore_<TICKER>_trend.png`
- Raw data: `zscore_<TICKER>.csv` and `.json`
- If a ticker is not available, only a `TICKER_NOT_AVAILABLE.txt` marker file will be present.

---

## Documentation & Release Process
- Version numbers and changelogs are up to date in documentation
- See `PLAN.md` and `TODO.md` for roadmap and actionable tasks
- See `LEARNINGS.md` for technical notes and known issues

---

## Key Features
- **Robust Data Fallback:** If yfinance fails to provide financials, the pipeline automatically falls back to SEC EDGAR/XBRL. If only partial data is available (e.g., only balance sheet, no income statement), the pipeline will transparently report this and explain why no Z-Score can be computed.
- **Transparent Error Reporting:** For tickers where only balance sheet data is available from SEC EDGAR (e.g., TUP), the output and logs will clearly state that no Z-Score can be computed due to missing income statement data.
- **Optimized LLM Integration:** Smart data trimming for SEC EDGAR and Yahoo Finance data reduces noise and token usage in LLM prompts while preserving essential information for analysis.
- **Centralized Model Logic:** All model coefficients and thresholds are stored in `src/altman_zscore/computation/constants.py`—no hard-coded values in the codebase. All model changes must be made in this file for transparency and maintainability.
- **Altman Z-Score Trend Analysis:** Computes and visualizes Z-Score trends for any US-listed company using real, live data
- **Industry-Aware Model Selection:** Automatically selects the correct Z-Score model based on SIC code, industry, region, and company maturity
- **Comprehensive Reporting:** Generates full, well-formatted reports (TXT, CSV, JSON) with context, formulas, diagnostics, and raw data mapping
- **Stock Price Overlay:** Visualizes Z-Score trends alongside historical stock prices
- **Robust Error Handling:** Clear diagnostics and error outputs for missing data, delisted tickers, or API issues. Now includes explicit user-facing errors for partial/insufficient financials.
- **Extensible Architecture:** Modular design for easy addition of new data sources, models, or output formats; ongoing work to modularize data connectors and prepare for web/REST/Excel interfaces

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
- See `PLAN.md` for the feature roadmap and major decisions
- See `TODO.md` for actionable tasks and environment setup
- Document significant learnings in `LEARNINGS.md`

---

## License
MIT (see LICENSE file)

---

For more details, see the full documentation in this repository and referenced files.
