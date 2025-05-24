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

## Roadmap & Feature Checklist

- [x] **MVP: Single-Stock Z-Score Trend Analysis**
  - [x] Deep analysis of a single stock
  - [x] Fetches and validates 3 years of quarterly financials
  - [x] Computes Altman Z-Score for each quarter, calibrated by industry/maturity
  - [x] Outputs Z-Score trend as table and plot
- [ ] **v1: Overlay Stock Price Trend**
  - [ ] Fetches and overlays stock price trend for the same period
  - [ ] Combined plot of Z-Score and price
- [ ] **v2: Sentiment & News Analysis**
  - [ ] Integrates sentiment analysis and news highlights
  - [ ] Correlates operational health from news/SEC filings with Z-Score and price
- [ ] **v3: Advanced Correlation & Insights**
  - [ ] Correlates Z-Score, price, and operational health metrics
  - [ ] Generates insights and alerts

<!--
## Future (Not in current roadmap)
- Portfolio Analysis: Generalizes pipeline to handle multiple tickers, batch analysis and reporting
-->

## Conservative, Incremental Rollout Policy
- Build a minimal, robust MVP first (single-stock Z-Score trend analysis).
- Test thoroughly at each step before enabling new features.
- Only enable new features after the MVP is stable and well-tested.
- Light up features one at a time, with tests and documentation, to avoid regressions.
- Avoid over-ambitious changes; prioritize reliability and maintainability.

## Documentation
- See `PLAN.md` for high-level vision, architecture, implementation steps, and major decisions.
- See `TODO.md` for actionable tasks, phase-specific work, and technical decisions.
- See `LEARNINGS.md` for key learnings and technical notes.

## License
MIT (see LICENSE file)

## Environment Variables & Secrets
- All API keys, user agents, and sensitive configuration are stored in the `.env` file at the project root.
- **Do not hardcode secrets or credentials in code or documentation.**
- Example `.env` entries:
  ```
  # SEC EDGAR Configuration
  SEC_EDGAR_USER_AGENT=AltmanZScore/1.0 (your@email.com) Python-Requests/3.0
  SEC_API_EMAIL=your@email.com
  ```
- Update the `.env` file as needed for new APIs or configuration.
- For Codespaces: The `.env` file is automatically loaded if present in the root directory.

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

See TODO.md and PLAN.md for roadmap and progress.
