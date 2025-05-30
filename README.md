# Altman Z-Score Analysis Platform

**Version: 2.4 (2025-05-30)**

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

**Release v2.4 (May 30, 2025):**
- Reporting layer always uses coefficients/thresholds from calculation (override_context)
- No hard-coded formulas or thresholds in reporting output
- Full fidelity for SIC/industry overrides and custom calibrations
- Model/threshold overrides and assumptions are logged in report
- All model constants and thresholds centralized in computation/constants.py
- Robust error handling and logging throughout pipeline

---

## Usage
To analyze a stock, run:
```sh
python main.py <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol (e.g., `AAPL`, `MSFT`).

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

## Short-Term Action Items (v2.4+)
- Add warnings for size/leverage outliers in the report
- Expand unit/integration tests for new model selection and reporting logic
- Integrate additional industry benchmark data (WRDS/Compustat or open data) into constants.py as available
- Document and automate calibration update process in altmans.md
- Schedule periodic calibration updates and document the process
- Continue to refine transparency and reporting for edge cases
- Expand FIELD_SYNONYMS and mapping logic for international/bank tickers (add multi-language, sector-aware mapping, and user overrides)
- Add/expand tests for prompt ingestion, mapping, and reporting
- Improve documentation for mapping, prompt usage, and internationalization
- Modularize data connectors and enhance CLI for batch/portfolio analysis
- Prepare for web dashboard, REST API, and Excel Add-In (see competition roadmap.md)

---

## Project Status & Roadmap
- **V2.4 (Current):** Reporting layer always uses coefficients/thresholds from calculation; no hard-coded formulas or thresholds in reporting output; full fidelity for SIC/industry overrides and custom calibrations; model/threshold overrides and assumptions are logged in report; all model constants and thresholds centralized in computation/constants.py; robust error handling and logging throughout pipeline
- **Short-Term (v2.4+):** See above action items for immediate priorities
- **V2.5 Roadmap:**
    - Forecasting: Add ability to forecast next quarter's Z-Score using consensus estimates and/or time series models
    - Sentiment & News Analysis: Integrate news and sentiment APIs, correlate with Z-Score and price trends
    - Portfolio/Multi-Ticker Analysis: Generalize pipeline for multiple tickers, output per-ticker and aggregate summaries
    - Testing & Documentation: Add/expand tests for new v2.5 features, update documentation for v2.5 features and usage
- **V2.2.2:** Script version included in every report; tested companies documentation and release process enforced; improved traceability
- **V2.2.1:** Prompt-driven reporting overhaul, user-editable prompt folder, improved attribution, robust report formatting
- **V2.2:** Model selection & calibration overhaul, enhanced visualizations

See `PLAN.md` and `TODO.md` for the full roadmap and actionable tasks.

---

## Key Features
- **Centralized Model Logic:** All model coefficients and thresholds are stored in `src/altman_zscore/computation/constants.py`—no hard-coded values in the codebase. All model changes must be made in this file for transparency and maintainability.
- **Altman Z-Score Trend Analysis:** Computes and visualizes Z-Score trends for any US-listed company using real, live data
- **Industry-Aware Model Selection:** Automatically selects the correct Z-Score model based on SIC code, industry, region, and company maturity
- **Comprehensive Reporting:** Generates full, well-formatted reports (TXT, CSV, JSON) with context, formulas, diagnostics, and raw data mapping
- **Stock Price Overlay:** Visualizes Z-Score trends alongside historical stock prices
- **Robust Error Handling:** Clear diagnostics and error outputs for missing data, delisted tickers, or API issues
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
