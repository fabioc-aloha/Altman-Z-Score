# Altman Z-Score Analysis Platform

**Version: 2.7 (2025-06-10)**

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

**Release v2.7 (June 10, 2025):**
- Robust fallback to SEC EDGAR for financials if yfinance fails
- Improved error reporting: pipeline now transparently reports when only balance sheet data is available (e.g., TUP), and no Z-Score can be computed due to missing income statement data
- Documentation and release process updated for new fallback and error handling features
- See PLAN.md for architectural decisions and LEARNINGS.md for edge cases

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
- All companies in `output/` are tracked in `output/TESTED_COMPANIES.md` (release-blocking)
- Version numbers and changelogs are up to date in documentation
- See `PLAN.md` and `TODO.md` for roadmap and actionable tasks
- See `LEARNINGS.md` for technical notes and known issues

---

## Short-Term Action Items (v2.7+)
- Review user feedback and bug reports from v2.7
- Implement improvements to LLM prompts and mapping logic based on feedback
- Plan next milestone features in PLAN.md
- Collect and prioritize user feedback for v2.8
- Draft v2.8 roadmap in PLAN.md
- Expand integration and regression tests for new logic
- Continue modularization and documentation of new features

---

## Project Status & Roadmap
- **V2.7 (Current):** Robust fallback to SEC EDGAR for financials, improved error reporting for balance-sheet-only cases, updated documentation and release process
- **Short-Term:** See above action items for immediate priorities
- **Planned/Future:**
    - Further LLM prompt tuning and mapping improvements
    - Additional data sources and advanced analytics
    - UI/UX improvements and web dashboard enhancements
    - Z-Score forecasting using consensus estimates and/or time series models
    - Sentiment & News Analysis: Integrate news and sentiment APIs, correlate with Z-Score and price trends
- **V2.6:** Z-Score forecasting, sentiment/news analysis, multi-ticker/portfolio support, modularized data connectors, advanced notifications, and expanded documentation/testing
- **V2.4:** Reporting layer always uses coefficients/thresholds from calculation; no hard-coded formulas or thresholds in reporting output; full fidelity for SIC/industry overrides and custom calibrations; model/threshold overrides and assumptions are logged in report; all model constants and thresholds centralized in computation/constants.py; robust error handling and logging throughout pipeline
- **V2.2.2:** Script version included in every report; tested companies documentation and release process enforced; improved traceability
- **V2.2.1:** Prompt-driven reporting overhaul, user-editable prompt folder, improved attribution, robust report formatting
- **V2.2:** Model selection & calibration overhaul, enhanced visualizations

See `PLAN.md` and `TODO.md` for the full roadmap and actionable tasks.

---

## Key Features
- **Robust Data Fallback:** If yfinance fails to provide financials, the pipeline automatically falls back to SEC EDGAR/XBRL. If only partial data is available (e.g., only balance sheet, no income statement), the pipeline will transparently report this and explain why no Z-Score can be computed.
- **Transparent Error Reporting:** For tickers where only balance sheet data is available from SEC EDGAR (e.g., TUP), the output and logs will clearly state that no Z-Score can be computed due to missing income statement data.
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
- Use Python 3.11+ (see `docs/venv_setup.md` for virtual environment instructions)

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
