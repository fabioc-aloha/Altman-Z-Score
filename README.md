# Altman Z-Score Analysis (2025+)

A modern, robust, and modular Python tool for deep single-stock Altman Z-Score trend analysis, designed for reliability, transparency, and extensibility. Built for professional and academic use, with a conservative, incremental rollout policy and a focus on best practices in quantitative and qualitative stock analysis.

## Project Description
- **Purpose:** Analyze the financial health and bankruptcy risk of a single public company over time using the Altman Z-Score, calibrated by industry and company maturity.
- **Scope:** Single-ticker analysis only (no portfolio support in current or near-term versions).
- **Data Sources:** SEC EDGAR (XBRL), Yahoo Finance, NewsAPI, and public industry benchmarks.
- **Tech Stack:** Python, pandas, pydantic, yfinance, sec-edgar-downloader, arelle/xbrlparse, matplotlib/plotly.
- **Best Practices:** Modular pipeline, strong validation, robust error handling, and full auditability/logging.
- **Codespaces Ready:** All development and testing is performed in GitHub Codespaces for reproducibility and ease of onboarding.

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
- See `PLAN.md` for high-level vision, architecture, and implementation steps.
- See `TODO.md` for actionable tasks and phase-specific work.
- See `DECISIONS.md` for architectural and data source decisions.
- See `LEARNINGS.md` for key learnings and technical notes.

## License
MIT (see LICENSE file)

## Archival of Previous Version
- The previous codebase, including all legacy scripts, tests, and documentation, has been moved to the `OLD/` directory.
- Refer to `OLD/README.md` for details on the contents and usage of the archived version.
- All new development, testing, and documentation should be performed in the root project directories and new `src/` structure.

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
