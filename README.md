# ---
# Indentation Best Practice:
# Always use 4 spaces per indentation level (never tabs). Configure your editor to insert spaces for tabs and display invisible characters. Use a linter (e.g., flake8) and autoformatter (e.g., black) to catch and fix indentation issues before running code. Set up pre-commit hooks to enforce this automatically.
# ---
# Altman Z-Score Analysis (Version 2.2)

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

**Project Status (as of May 29, 2025):**
- **V2.2 (Current):** Model selection & calibration overhaul, enhanced visualizations with improved plotting features
- **V2.1:** Stable Z-Score trend analysis, robust reporting, per-ticker outputs, and codebase cleanup
- **V2.0.2 (Publishing Issue):** Complete
- **V2.0.1 (Bug Fix & Resilience Improvement):** Complete
- **MVP (Single-Stock Z-Score Trend Analysis):** Complete and stable
- **v1 (Stock Price Overlay):** Complete
- **v2 (Per-ticker outputs, main.py entry point, codebase cleanup):** Complete and merged to main
- **v2.5 (Forecasting, Sentiment, Portfolio Analysis):** In planning (see PLAN.md)
- All development and testing uses a local Python 3.11+ virtual environment (`.venv`)

---

## Version Roadmap
- **V2.1 (Current):** Stable Z-Score trend analysis, robust reporting, per-ticker outputs, and codebase cleanup.
- **V2.2:** Model selection & calibration overhaul (maturity, IPO, industry, region, centralized constants, transparency, extensibility).
- **V2.5:** Z-Score forecasting, sentiment/news analysis, and advanced plotting.
- **V2.6:** Portfolio/multi-ticker analysis.
- **V2.7:** Advanced correlation and insights.
- **V2.8:** Community contributions and plugin support.

---

## Output Examples
The repository includes example reports in the `output/` directory. Each example shows:
- Time series Z-Score calculation with trend analysis
- Financial health assessment with industry context
- Enhanced visualizations with Z-Score and stock price overlay
- Raw data files (CSV/JSON) with mapped financial fields
- Comprehensive markdown and DOCX reports

These examples demonstrate the format and quality of analysis you can expect when running the tool on any publicly traded company.

---

## Output Examples
The repository includes example reports in the `output/` directory for MSFT, RIVN, SONO, and TSLA. Each example shows:
- Time series Z-Score calculation with trend analysis
- Financial health assessment with industry context
- Enhanced visualizations with Z-Score and stock price overlay
- Raw data files (CSV/JSON) with mapped financial fields
- Comprehensive markdown reports

These examples demonstrate the format and quality of analysis you can expect when running the tool on any publicly traded company.

---

## V2.0.2: Publishing Issue
- No code changes. This release addresses a publishing/tagging issue on GitHub only.

## V2.0.1: Bug Fix & Resilience Improvement
- All output file and directory creation is now fully centralized and robust (no hardcoded paths).
- If a ticker is invalid or unavailable, a clear marker file (`TICKER_NOT_AVAILABLE.txt`) is written in the output folder, and no other files are created.
- Removed all legacy, redundant, or confusing output files (component tables, summary, profile, etc.).
- Documentation and code comments have been updated for clarity and maintainability.
- The codebase is now more robust to edge cases and easier to maintain.

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
- Trend chart: `zscore_<TICKER>_trend.png`
- Raw data: `zscore_<TICKER>.csv` and `.json`
- If a ticker is not available or does not exist, only a `TICKER_NOT_AVAILABLE.txt` marker file will be present in the output folder.

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
- **Batch/Portfolio Analysis:** (Planned for v2.6+) Analyze multiple tickers or portfolios with a single command
- **Forecasting & Sentiment:** (v2.5 Roadmap) Integrate consensus estimates and news sentiment for forward-looking risk analysis

---

## Roadmap
- [x] MVP: Single-Stock Z-Score Trend Analysis
- [x] v1: Overlay Stock Price Trend
- [x] v2: Enhanced Reporting (Full report file generation)
- [ ] v2.5: Sentiment & News Analysis
- [ ] v2.6: Portfolio Analysis
- [ ] v2.7: Advanced Correlation & Insights

---

## Environment Setup
- Copy `.env.example` to `.env` and fill in your API keys and configuration
- Install dependencies:
  ```pwsh
  pip install -r requirements.txt
  ```
- Use Python 3.11+ with a `.venv` virtual environment (see `docs/venv_setup.md` for setup instructions)

### Environment Variables
The project uses a `.env` file in the root directory to manage API keys and configuration. For security, your real `.env` should never be committed to version control. Instead, use the provided `.env.example` as a template:

1. Copy `.env.example` to `.env` in the project root.
2. Fill in your real credentials and configuration values.

Example:
```
SEC_EDGAR_USER_AGENT=AltmanZScore/1.0 (your@email.com) Python-Requests/3.0
SEC_API_EMAIL=your@email.com
```

### Python Virtual Environment Setup
- This project uses a Python virtual environment (`.venv`) for dependency management and isolation.
- Requires Python 3.11+.
- See `docs/venv_setup.md` for detailed instructions on setting up and activating the virtual environment.

---

## Usage

### Setup
1. Install Python 3.11+ if not already installed.
2. Activate your `.venv` and install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure your `.env` file as described above.

### Run Analysis
To analyze a stock, use the CLI in `main.py`:
```sh
python main.py <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol you want to analyze (e.g., `AAPL`, `MSFT`).

#### Example
```sh
python main.py MSFT --start 2023-01-01
```
This will generate the Z-Score trend analysis for Microsoft starting from January 1, 2023, and save the results in the `output/` directory.

---

## DOCX Export: Markdown to Word Conversion

This project includes a utility to convert the full Markdown report to a Word (DOCX) document, preserving all formatting, tables, images, and charts. This is useful for sharing, printing, or further editing your analysis in Microsoft Word or Google Docs.

**How to use:**

1. Generate your Markdown report as usual (e.g., `output/SONO/zscore_SONO_zscore_full_report.txt`).
2. Use the provided function:

```python
from altman_zscore.md_to_docx import convert_report_md_to_docx
convert_report_md_to_docx('output/SONO/zscore_SONO_zscore_full_report.txt')
```

- The output will be saved as `output/SONO/zscore_SONO_zscore_full_report.docx` by default.
- All Markdown features (headings, tables, lists, blockquotes, images) are supported.
- Charts and images referenced in the Markdown will be embedded in the DOCX if available.

**Feature highlights:**
- Converts Markdown to DOCX, preserving all formatting and structure
- Embeds images and charts
- Output is suitable for professional reporting and further editing

---

## Outputs
- **Full Analysis Report**: `output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt`
- **Raw Data**: CSV and JSON files for Z-Score components and price data.
- **Trend Chart**: `output/<TICKER>/zscore_<TICKER>_trend.png` with enhanced price overlay.
- If a ticker is not available or does not exist, only a `TICKER_NOT_AVAILABLE.txt` marker file will be present in the output folder.

---

## Known Limitations
- **SIC/Industry Mapping**: May not always reflect true business maturity.
- **Quarterly Data Gaps**: Missing or irregular filings may result in gaps.
- **International Companies**: Designed for US-listed equities; non-US companies may have incomplete data.
- **Portfolio Analysis**: Only single-ticker analysis is supported.
- **Data Source Reliability**: Dependent on public APIs; outages may affect functionality.

For more details, see `LEARNINGS.md` and the project Wiki.

---

## Development & Contribution
- All changes must pass existing and new tests.
- New features require updated tests and documentation.
- See `PLAN.md` for the feature roadmap and major decisions.
- See `TODO.md` for actionable tasks and environment setup.
- Document significant learnings in `LEARNINGS.md`.

## Test & Development Environment
- The project uses a `src/` layout. For all tests and scripts to work, you must ensure `PYTHONPATH=src` is set in your environment.
- This is set in the `.env` file, but most shells (including PowerShell) do **not** auto-load `.env` for environment variables.
- **To run tests in PowerShell:**
  ```powershell
  $env:PYTHONPATH="src"; pytest
  ```
- **To run tests in bash:**
  ```bash
  export PYTHONPATH=src; pytest
  ```
- Codespaces and some IDEs may auto-load `.env`, but if you see `ModuleNotFoundError: No module named 'altman_zscore'`, set `PYTHONPATH` manually as above.

## License
MIT (see LICENSE file)

## Changelog

### V2.1 (May 28, 2025) — Current
- Stable Z-Score trend analysis, robust reporting, per-ticker outputs, and codebase cleanup.

### V2.0.2 (May 28, 2025) — Publishing Issue
- No code changes. This release addresses a publishing/tagging issue on GitHub only.

### V2.0.1 (May 28, 2025) — Bug Fix & Resilience Improvement
- All output file and directory creation is now fully centralized and robust (no hardcoded paths).
- If a ticker is invalid or unavailable, a clear marker file (`TICKER_NOT_AVAILABLE.txt`) is written in the output folder, and no other files are created.
- Removed all legacy, redundant, or confusing output files (component tables, summary, profile, etc.).
- Documentation and code comments have been updated for clarity and maintainability.
- The codebase is now more robust to edge cases and easier to maintain.

## Recent Improvements (May 2025)
- **Advanced Model Selection:**
  - Z-Score model selection now incorporates company age, IPO date, industry (SIC), public/private status, and region.
  - Maturity is classified as early-stage, growth, or mature using founding year and IPO date.
  - Industry-specific and region-specific (EM) models and thresholds are supported.
- **Centralized Constants:**
  - All model coefficients and thresholds are now stored in `src/altman_zscore/computation/constants.py`.
  - No hard-coded values remain in the codebase; all logic references the centralized constants.
- **Transparency and Reporting:**
  - The report now logs all model/threshold overrides and lists assumptions and rationale for model selection.
  - Warnings are added for size/leverage outliers.
- **Extensibility:**
  - The architecture supports easy addition of new models, coefficients, and thresholds via `constants.py`.
  - Calibration data is versioned and traceable.
- **Documentation:**
  - A detailed plan for further improvements and calibration is maintained in `altmans.md`.

## Version Roadmap
- **V2.1 (Current):** Stable Z-Score trend analysis, robust reporting, per-ticker outputs, and codebase cleanup.
- **V2.2:** Model selection & calibration overhaul (maturity, IPO, industry, region, centralized constants, transparency, extensibility).
- **V2.5:** Z-Score forecasting, sentiment/news analysis, and advanced plotting.
- **V2.6:** Portfolio/multi-ticker analysis.
- **V2.7:** Advanced correlation and insights.
- **V2.8:** Community contributions and plugin support.
