# Altman Z-Score Analysis (2025+)

A modern, robust, and modular Python tool for deep single-stock Altman Z-Score trend analysis, designed for reliability, transparency, and extensibility. Built for professional and academic use, with a conservative, incremental rollout policy and a focus on best practices in quantitative and qualitative stock analysis.

---
**Project Status (as of May 24, 2025):**
- **MVP (Single-Stock Z-Score Trend Analysis) is complete and stable.**
- All reporting, charting, and error handling features for the MVP are implemented and tested.
- The project is now focused on **v1: Overlay Stock Price Trend** (in progress).
- All development and testing is performed in GitHub Codespaces and is fully compatible.
- Documentation, testing, and incremental rollout policies are strictly followed.
---

## Project Description
- **Purpose:** Analyze the financial health and bankruptcy risk of a single public company over time using the Altman Z-Score, calibrated by industry and company maturity.
- **Scope:** Single-ticker analysis only (no portfolio support in current or near-term versions).
- **Data Sources:** SEC EDGAR (XBRL), Yahoo Finance, NewsAPI, and public industry benchmarks.
- **Tech Stack:** Python, pandas, pydantic, yfinance, sec-edgar-downloader, arelle/xbrlparse, matplotlib/plotly.
- **Best Practices:** Modular pipeline, strong validation, robust error handling, and full auditability/logging.
- **Local Development:** Now uses a local Python virtual environment (`.venv`). See `docs/venv_setup.md` for setup instructions.

## Altman Z-Score Computation Pipeline (MVP)

This project provides a robust, modular, and testable pipeline for single-stock Altman Z-Score trend analysis, designed for professional, research, and educational use. The MVP release focuses on clarity, reliability, and extensibility, with a strong emphasis on error handling and user experience.

### Key Features
- **Single-Stock Z-Score Trend Analysis**: Computes and visualizes Altman Z-Score trends for any US-listed equity using only real, live data (no static/hardcoded values).
- **Robust Error Handling**: Gracefully handles delisted, missing, or invalid tickers (e.g., RIDE, JHKASD), saving user-friendly error reports and exiting cleanly without stack traces.
- **Minimal Console Output**: Only essential information, warnings, and errors are shown; all debug output is suppressed.
- **Comprehensive Reporting**: Output files and charts include company profile, SIC code, and model details in footnotes.
- **Professional Documentation**: All core modules have complete module-level docstrings, public functions/classes are fully documented, and non-obvious logic is explained with inline comments.
- **Environment Flexibility**: Compatible with both GitHub Codespaces and local Python virtual environments. See `docs/venv_setup.md` for local setup instructions. Uses `pyproject.toml` for dependencies.
- **Extensible Architecture**: Clean separation of input, data fetching, validation, computation, and reporting layers. Easy to add new models, data sources, or output formats.

### Project Structure
- `src/altman_zscore/one_stock_analysis.py`: Main pipeline, CLI, output, error handling, docstrings
- `src/altman_zscore/plotting.py`: Chart/plot output, legend, docstrings
- `src/altman_zscore/fetch_financials.py`: Financials fetching, fallback logic, docstrings
- `src/altman_zscore/company_profile.py`: Profile classification, fallback logic, docstrings
- `src/altman_zscore/data_validation.py`: Validation, diagnostics, docstrings
- `src/altman_zscore/compute_zscore.py`: Z-Score computation, model selection, docstrings
- `README.md`, `PLAN.md`, `TODO.md`, `docs/venv_setup.md`: Project documentation

### Usage
1. **Setup**: See `docs/venv_setup.md` and `.env.example` for environment and API key setup.
2. **Run Analysis**: Use the CLI in `one_stock_analysis.py` to analyze a ticker:
   ```sh
   python -m src.altman_zscore.one_stock_analysis --ticker AAPL
   ```
3. **Outputs**: Results are saved to CSV, JSON, and PNG files in the `output/` directory, with clear error reports for any failures.

### Updated Entry Point

The main entry point for running the Altman Z-Score analysis pipeline is now `altman_zscore.py`. This script provides a streamlined interface for analyzing single-stock Z-Score trends.

#### Usage
To analyze a stock, run the following command:
```sh
python altman_zscore.py --ticker <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol you want to analyze (e.g., `AAPL`, `MSFT`).

#### Example
```sh
python altman_zscore.py --ticker MSFT
```
This will generate the Z-Score trend analysis for Microsoft and save the results in the `output/` directory.

### Development & Contribution
- All changes must pass existing and new tests.
- New features require new or updated tests and documentation.
- See `PLAN.md` for the feature roadmap and major decisions.
- See `TODO.md` for actionable tasks and environment setup.
- Document significant learnings in `LEARNINGS.md`.
- If you wish to contribute, please follow the modularity, testability, and documentation standards established in the codebase.

### Roadmap
- [x] MVP: Single-Stock Z-Score Trend Analysis
- [ ] v1: Overlay Stock Price Trend
- [ ] v2: Sentiment & News Analysis
- [ ] v3: Portfolio Analysis
- [ ] v4: Advanced Correlation & Insights

## License
MIT (see LICENSE file)

## Environment Setup

### Environment Variables

The project uses a `.env` file in the root directory to manage API keys and configuration. For security, your real `.env` should never be committed to version control. Instead, use the provided `.env.example` as a template:

- Copy `.env.example` to `.env` in the project root.
- Fill in your real credentials and configuration values.
- The most important variables are:

    - `SEC_EDGAR_USER_AGENT`: Required. Your SEC EDGAR User-Agent string (format: `Project/Version (your@email.com) Python-Requests/3.0`).
    - `SEC_API_EMAIL`: Required. Your contact email for SEC API access.

- Optional variables are provided for additional data sources (Yahoo Finance, NewsAPI, etc.) and cache configuration.

Example:

```
SEC_EDGAR_USER_AGENT=AltmanZScore/1.0 (your@email.com) Python-Requests/3.0
SEC_API_EMAIL=your@email.com
```

See `.env.example` for all available options and documentation.

## Python Virtual Environment Setup
- This project uses a Python virtual environment (`.venv`) for dependency management and isolation.
- See `docs/venv_setup.md` for detailed instructions on setting up and activating the virtual environment.

## Key Features Implemented (as of May 24, 2025)
- Single-stock Z-Score analysis pipeline: end-to-end, from input to reporting
- Industry classification: yfinance, SEC EDGAR, and static patterns for robust mapping
- Model selection: automatic based on company profile
- Data validation: Pydantic schemas for all financial data
- Computation: Altman Z-Score for each quarter, robust error handling
- Reporting:
  - CSV and JSON output for each analysis run (saved to output/)
  - Z-Score trend plot as PNG, with risk zone bands, value labels, quarter-based x-axis, and a robust legend showing all risk zones and thresholds (saved to output/)
  - Company profile, SIC code, and model details included as a footnote in the chart
  - Output directory is created if missing; absolute path to chart is printed after saving
- Edge-case handling: improved classification and error reporting for tickers like SONO and YHOO
- Note: Rivian (RIVN) is a well-known, high-profile growth-stage company in the EV sector. It is classified as "mature" due to SIC 3711 (Motor Vehicles) for model selection purposes, but this does not reflect its true business maturity, age, or profitability. This is not a forensic or obscure edge case, but a limitation of SIC-based mapping for model selection.
- Tested tickers: MSFT, AAPL, SONO, YHOO (outputs verified)
- Modular code: plotting logic in src/altman_zscore/plotting.py
- Local development: all work in a local .venv (see docs/venv_setup.md)

## How to Run
1. Activate your .venv and install dependencies (pip install -r requirements.txt)
2. Run the analysis script (see README.md for CLI usage)
3. Find all outputs (CSV, JSON, PNG) in the output/ folder. The absolute path to the chart is printed after each run.

## Tested and Working
- Chart output is visually clear, robust, and user-friendly, with a complete legend and footnote
- All reporting files are generated and saved as expected
- Output directory is created if missing
- All improvements are reflected in the codebase and documentation

## Community & Documentation

- This repository is public as of May 2025.
- The GitHub Wiki is enabled for extended documentation, guides, and community contributions.
- See the Wiki tab above for more details, usage examples, and technical notes.

See TODO.md and PLAN.md for roadmap and progress.

## Known Limitations & Edge Cases

### Delisted and Nonexistent Companies
- The pipeline uses only real, live data from SEC EDGAR and Yahoo Finance. If a ticker is delisted, has changed symbols, or is not found in public data sources, the analysis will fail gracefully and save a user-friendly error report. However, for some delisted companies, especially those with no recent filings or market data, it may not be possible to retrieve any financials or price history. In these cases, the output will indicate the data gap and the analysis will not proceed.
- Some tickers (e.g., RIDE, JHKASD) may have partial or missing data due to the timing of delisting, bankruptcy, or symbol changes. The pipeline will report these cases clearly, but cannot fill in missing data from static or unofficial sources.
- If a company has changed its ticker or CIK, you may need to research the new symbol or CIK manually.

### Other Limitations
- **SIC/Industry Mapping**: Model selection is based on SIC code and industry mapping from public sources. This may not always reflect the true business maturity or sector (e.g., Rivian is classified as "mature" due to SIC 3711, but is a growth-stage company).
- **Quarterly Data Gaps**: If a company has missing or irregular quarterly filings, the Z-Score trend may have gaps or fewer data points.
- **International Companies**: The pipeline is designed for US-listed equities. Non-US companies or ADRs may have incomplete or inconsistent data.
- **Portfolio Analysis**: Only single-ticker analysis is supported in the MVP. Portfolio and multi-ticker support is planned for future versions.
- **News/Sentiment**: Sentiment and news analysis are not included in the MVP, but are planned for future releases.
- **Data Source Reliability**: All results depend on the accuracy and availability of public APIs and data sources. Outages or changes in data provider APIs may temporarily affect functionality.

For more details on edge cases and technical learnings, see `LEARNINGS.md` and the project Wiki.
