# Altman Z-Score Analysis (V2)

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---
<<<<<<< HEAD

## Project Status (May 2025)
- **MVP (Single-Stock Z-Score Trend Analysis):** Complete and stable
- **v1 (Stock Price Overlay):** Complete
- **v2 (Per-ticker outputs, main.py entry point, codebase cleanup):** Complete and merged to main
- **v2.5 (Forecasting, Sentiment, Portfolio Analysis):** In planning (see PLAN.md)
- All development and testing uses a local Python 3.11+ virtual environment (`.venv`)

=======
**Project Status (as of May 27, 2025):**
- **May 2025 Update:**
  - Added monthly stock price statistics with whisker overlay for better price trend visualization
  - Experimental AI parsing features have been removed to focus on a robust, traditional pipeline.
  - The financials fetching logic now includes extensive fallback field mappings (notably for TSLA and AAPL), ensuring that quarters are only skipped when data is truly missing.
  - The codebase is now simpler, more maintainable, and focused on reliability and transparency.
- **MVP (Single-Stock Z-Score Trend Analysis) is complete and stable.**
- All reporting, charting, and error handling features for the MVP are implemented and tested.
- **v1: Overlay Stock Price Trend** is partially complete - price overlay now working correctly.
- The project is now focused on the Z-Score forecasting feature for v1 completion.
- All development and testing is performed in GitHub Codespaces and is fully compatible.
- Documentation, testing, and incremental rollout policies are strictly followed.
>>>>>>> 671cc1f (Refactor: remove deprecated files, clean up diagnostics output, and clarify main entry point. All outputs now organized per ticker. Deprecated modules removed.)
---

## What Does This Project Do?
- **Purpose:** Analyze the financial health and bankruptcy risk of a public company over time using the Altman Z-Score, with industry-aware model selection.
- **Scope:** Single-ticker analysis (portfolio/multi-ticker coming in v2.5+)
- **Data Sources:** SEC EDGAR (XBRL), Yahoo Finance, NewsAPI, public industry benchmarks
- **Tech Stack:** Python, pandas, pydantic, yfinance, sec-edgar-downloader, xbrlparse, matplotlib/plotly

---

## Key Features
- **Altman Z-Score Trend Analysis:** Computes and visualizes Z-Score trends for any US-listed company using real, live data
- **Industry-Aware Model Selection:** Automatically selects the correct Z-Score model based on SIC code and industry
- **Comprehensive Reporting:** Generates full, well-formatted reports (TXT, CSV, JSON) with context, formulas, diagnostics, and raw data mapping
- **Stock Price Overlay:** Visualizes Z-Score trends alongside historical stock prices
- **Robust Error Handling:** Clear diagnostics and error outputs for missing data, delisted tickers, or API issues
- **Extensible Architecture:** Modular design for easy addition of new data sources, models, or output formats

<<<<<<< HEAD
---
=======
### Key Features
- **Single-Stock Z-Score Trend Analysis**: Computes and visualizes Altman Z-Score trends for any US-listed equity using only real, live data (no static/hardcoded values).
- **Enhanced Price Trend Visualization**: Features monthly price statistics overlay with whiskers showing:
  - Monthly average price points
  - High-low ranges visualized as whiskers
  - Transparent overlay for easy Z-Score trend comparison
  - Per-month data point counts for transparency
- **Robust Error Handling**: Gracefully handles delisted, missing, or invalid tickers (e.g., RIDE, JHKASD), saving user-friendly error reports and exiting cleanly without stack traces.
- **Minimal Console Output**: Only essential information, warnings, and errors are shown; all debug output is suppressed.
- **Comprehensive Reporting**: Output files and charts include company profile, SIC code, and model details in footnotes.
- **Full Analysis Report Output**: For each analysis, a comprehensive, well-formatted report is generated and saved as `output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt`. This file includes:
  - Context and model selection details
  - Raw data field mapping table (values in millions of USD)
  - Z-Score component table with risk area diagnostics for each quarter
  - All formulas and calculation details
  - This is the main reference for interpreting results and auditability.
- **Other Output Files**:
  - `output/<TICKER>/zscore_<TICKER>_summary.txt`: Table summary of all computed quarters
  - `output/<TICKER>/zscore_<TICKER>_profile.txt`: Company profile and classification
  - `output/<TICKER>/zscore_<TICKER>.csv` and `.json`: Raw results for further analysis
  - `output/<TICKER>/quarterly_prices_<TICKER>.csv` and `.json`: Quarterly price data used in the analysis
  - `output/<TICKER>/monthly_prices_<TICKER>.csv` and `.json`: Monthly price statistics (avg, min, max)
  - `output/<TICKER>/zscore_<TICKER>_trend.png`: Z-Score trend chart with enhanced price overlay and monthly statistics
- **Professional Documentation**: All core modules have complete module-level docstrings, public functions/classes are fully documented, and non-obvious logic is explained with inline comments.
- **Environment Flexibility**: Compatible with both GitHub Codespaces and local Python virtual environments. See `docs/venv_setup.md` for local setup instructions. Uses `pyproject.toml` for dependencies.
- **Extensible Architecture**: Clean separation of input, data fetching, validation, computation, and reporting layers. Easy to add new models, data sources, or output formats.
>>>>>>> 671cc1f (Refactor: remove deprecated files, clean up diagnostics output, and clarify main entry point. All outputs now organized per ticker. Deprecated modules removed.)

## Usage
To analyze a stock, run:
```pwsh
python main.py <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol you want to analyze (e.g., `AAPL`, `MSFT`).

Example:
```pwsh
python main.py AAPL
```

Outputs will be saved in the `output/<TICKER>/` directory:
- Full report: `zscore_<TICKER>_zscore_full_report.txt`
- Component table: `zscore_<TICKER>_zscore_components.txt`
- Trend chart: `zscore_<TICKER>_trend.png`
- Raw data: `zscore_<TICKER>.csv` and `.json`
- Profile/summary: `zscore_<TICKER>_profile.txt`

Reports include mapped industry, SIC code, model selection rationale, and risk diagnostics for each quarter. Charts show Z-Score trends with risk zones and optional price overlay.

---

## Typical Workflow
1. **Clone the Repository**
2. **Set Up Your Environment** (see below)
3. **Run the Analysis Pipeline** for a ticker (see Usage above)
4. **Review Outputs** in the output directory
5. **Interpret Results** using the generated reports and charts

---

## Advanced Usage
- **Custom Analysis:** Extend the pipeline to new models, data sources, or output formats by following the modular structure
- **Batch/Portfolio Analysis:** (Planned for v2.5+) Analyze multiple tickers or portfolios with a single command
- **Forecasting & Sentiment:** (v2.5 Roadmap) Integrate consensus estimates and news sentiment for forward-looking risk analysis

---

## Environment Setup
- Copy `.env.example` to `.env` and fill in your API keys and configuration
- Install dependencies:
  ```pwsh
  pip install -r requirements.txt
  ```
- Use Python 3.11+ with a `.venv` virtual environment (see `docs/venv_setup.md` for setup instructions)

---

## Documentation & Support
- See `PLAN.md` and `TODO.md` for roadmap, progress, and technical decisions
- The GitHub Wiki provides extended guides, usage examples, and troubleshooting
- For questions or contributions, open an issue or pull request on GitHub

---

MVP, v1, and v2 are complete as of May 2025. v2.5 (forecasting, sentiment, portfolio analysis) is in planning—see PLAN.md for details.
