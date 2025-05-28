# Altman Z-Score Refactor Plan (2025, Revised)

## May 2025 Update

- Removed experimental AI parsing features (`srcai/`, `ai_bootstrap.py`) to focus on a robust, traditional pipeline.
- Improved fallback logic for field name variations in SEC/XBRL and Yahoo Finance data (notably for TSLA and AAPL).
- Quarters with missing filings are now skipped early, reducing noise and improving reliability.
- All major architectural and technical decisions are tracked here and in TODO.md.
- Enhanced reporting: always show industry name (mapped from SIC code) in all reports
- Context section now combines industry and SIC code into a single line
- Z-Score Component Table's Diagnostic column displays the risk area (Safe Zone, Distress Zone, Grey Zone) for each quarter
- All output is clearer, well-formatted, and robust, with improved field mapping and value formatting
- Full analysis report is saved as output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt; other key output files: summary, profile, CSV/JSON, and trend chart for each ticker

## May 2025: Recent Accomplishments
- Robust reporting: Industry name (mapped from SIC) always shown; context line combines industry and SIC; Z-Score Component Table's Diagnostic column shows risk area for each quarter.
- Full, well-formatted analysis report saved as output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt; all key output files (summary, profile, CSV/JSON, trend chart) documented in README.
- All core docstrings and comments reviewed and updated for clarity, accuracy, and maintainability (compute_zscore, plotting, analysis, etc.).
- Type safety: Model selection and all function signatures now robust to static analysis; Pylance errors resolved.
- Documentation and planning (README, TODO.md, PLAN.md) fully up to date.
- v1 (Stock Price Overlay) is complete, stable, and well-tested. All MVP goals met.

---

## v2 Roadmap: Z-Score Forecasting & Sentiment Analysis

### Immediate Next Steps
1. **Requirements Review**: Finalize requirements for Z-Score forecasting (define data sources, model, and output format).
2. **API Research**: Evaluate and select APIs for consensus estimates and news/sentiment (Yahoo Finance, NewsAPI, others).
3. **Design**: Draft a lightweight, explainable, and robust forecasting model. Define clear interfaces for new modules.
4. **Scaffolding**: Scaffold new modules for forecasting and sentiment analysis, following the established modular/testable pattern.
5. **Testing**: Add/expand tests for all new v2 features. Ensure v1 features remain stable and well-tested during v2 development.
6. **Documentation**: Update README, PLAN.md, and TODO.md for v2 features, usage, and architecture.

### Guiding Principles for v2
- Maintain modularity, testability, and robust error handling throughout.
- Each v2 feature phase should be independently testable and deliver incremental value.
- Preserve Codespaces compatibility and document all new dependencies or environment changes.
- Continue to use PLAN.md and TODO.md for tracking major decisions and actionable tasks.

---

## v2 Feature Goals
- Z-Score forecasting using consensus estimates and/or time series models
- News and sentiment integration for risk/diagnostic context
- Extensible architecture for future portfolio/multi-ticker analysis
- Maintain and improve reporting, error handling, and documentation standards

## Background
This plan is based on the new concept outlined in `OneStockAnalysis.md` and incorporates Altman's Z-Score model documentation. The goal is to create a robust, modular, and testable Altman Z-Score analysis tool for single stocks and portfolios, with a focus on reliability, data integrity, and ease of maintenance.

## High-Level Goals
- **Simplicity:** Start with a single-stock analysis pipeline, then generalize to portfolios.
- **Modularity:** Clean separation of data fetching, validation, computation, and reporting.
- **Testability:** Each module is independently testable with clear interfaces.
- **Robustness:** Strong error handling, logging, and data validation at every step.
- **Extensibility:** Easy to add new data sources, models, or output formats.
- **Best Practices:** Use industry/maturity calibration, and follow professional analyst standards.

## Architecture Overview
1. **Input Layer**
   - Accepts a ticker (or list of tickers) and analysis date.
   - Validates input format and existence.
   - Optionally accepts industry and company maturity overrides.
2. **Data Fetching Layer**
   - Fetches financials from SEC EDGAR (XBRL) using `sec-api` or `sec-edgar-downloader`.
   - Parses XBRL using `xbrlparse` (latest maintained).
   - Fetches market data from Yahoo Finance using `yfinance`.
   - Optionally fetches industry/maturity benchmarks from public datasets (e.g., WRDS, Compustat, or open data).
3. **Validation Layer**
   - Validates raw data using Pydantic schemas.
   - Reports missing/invalid fields and halts or warns as appropriate.
   - Ensures all Z-Score components are present and reasonable.
4. **Computation Layer**
   - Computes Altman Z-Score using validated data.
   - Calibrates Z-Score by industry and company maturity (using latest academic coefficients and benchmarks).
   - Returns result object with all intermediate values, calibration details, and errors.
5. **Reporting Layer**
   - Outputs results to CSV, JSON, or stdout.
   - Plots Z-Score trend (matplotlib/plotly).
   - Logs all steps and errors for traceability.
   - (v1) Overlays price trend; (v2) overlays sentiment/news.

## Implementation Steps
1. **Bootstrap New Codebase**
   - Scaffold `src/altman_zscore/one_stock_analysis.py` for the single-stock pipeline.
   - Use only minimal, modern dependencies (`pandas`, `requests`, `pydantic`, `yfinance`, `sec-api`, `xbrlparse`, `matplotlib`/`plotly`).
2. **Implement Input & Config Handling**
   - Parse CLI args or function params for ticker, date, industry, and maturity.
   - Validate inputs.
3. **Implement Data Fetching**
   - Write `fetch_sec_financials(ticker, date)` using `sec-api` or `sec-edgar-downloader`.
   - Parse XBRL with `xbrlparse`.
   - Write `fetch_yahoo_market_data(ticker, date)` using `yfinance`.
   - Fetch industry/maturity benchmarks if available.
4. **Implement Validation Schemas**
   - Create Pydantic models in `schemas/validation.py` for all expected data.
   - Validate fetched data and report issues.
5. **Implement Z-Score Computation**
   - Write a pure function `compute_zscore(validated_data, industry, maturity)`.
   - Use latest Altman Z-Score models (original, emerging markets, service, private, etc.).
   - Calibrate coefficients and thresholds by industry and maturity.
   - Return result object with all components and calibration details.
6. **Implement Reporting**
   - Output result to CSV/JSON and log all steps.
   - Plot Z-Score trend (matplotlib/plotly).
   - (v1) Overlay price trend; (v2) overlay sentiment/news.
   - **Generate full analysis report as output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt, including context, field mapping, Z-Score component table with risk area, and all formulas.**
   - **Ensure all output is robust, well-formatted, and includes all key context and diagnostics.**
7. **Testing**
   - Write unit tests for each module.
   - Add integration test for the full pipeline.
8. **Iterate and Generalize**
   - Once single-stock works, generalize to portfolio analysis.
   - Refactor as needed for extensibility and maintainability.

## Best Practices & Analyst Guidance
- **Data Quality:** Always validate and cross-check financials; flag outliers and missing data.
- **Calibration:** Use industry and maturity-specific Z-Score coefficients and thresholds (see latest Altman research and WRDS/Compustat/academic sources).
- **Documentation:** Clearly document all assumptions, calibration sources, and limitations.
- **Transparency:** Log all data sources, errors, and calibration steps for auditability.
- **Testing:** Use real-world tickers and edge cases in tests.

## Feature Roadmap

- [x] **MVP: Single-Stock Z-Score Trend Analysis**
  - Deep analysis of a single stock
  - Fetches and validates 3 years of quarterly financials
  - Computes Altman Z-Score for each quarter, calibrated by industry/maturity
  - Outputs Z-Score trend as table and plot, with robust legend and company profile/model footnote (MVP complete as of May 24, 2025)
- [x] **v1: Overlay Stock Price Trend** (Complete as of May 27, 2025)
  - [x] Fetches and overlays stock price trend for the same period
  - [x] Combined plot of Z-Score and price
  - [x] Fixed date formatting issue in price fetching function to handle datetime strings with time components
- [ ] **v2: Z-Score Forecasting & Sentiment Analysis**
  - [ ] **Z-Score Forecasting Feature:**
    - **Objective:** Add the ability to forecast the next quarter's Z-Score based on consensus estimates and other data sources.
    - **Implementation Steps:**
      1. **Data Collection:**
         - Fetch consensus estimates for key financial metrics (e.g., revenue, EBITDA, net income) from Yahoo Finance or other APIs.
         - Integrate additional data sources for industry trends and macroeconomic indicators.
      2. **Forecasting Model:**
         - Develop a lightweight forecasting model to estimate Z-Score components based on collected data.
         - Use historical trends and industry benchmarks to refine predictions.
      3. **Integration:**
         - Extend the computation layer to include forecasted Z-Score values.
         - Update the reporting layer to display forecasted Z-Score alongside historical trends.
      4. **Validation:**
         - Test the forecasting feature with multiple tickers to ensure accuracy and reliability.
      5. **Documentation:**
         - Update README.md and other documentation to include usage instructions and limitations for the forecasting feature.
  - [ ] Integrates sentiment analysis and news highlights
  - [ ] Correlates operational health from news/SEC filings with Z-Score and price
- [ ] **v2: Sentiment & News Analysis**
  - Integrates sentiment analysis and news highlights
  - Correlates operational health from news/SEC filings with Z-Score and price
- [ ] **v3: Advanced Correlation & Insights**
  - Correlates Z-Score, price, and operational health metrics
  - Generates insights and alerts

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

## Project Guidance
- Use this PLAN.md for high-level features, vision, and progress tracking.
- Use TODO.md for actionable tasks, environment setup, and phase-specific work.
- All development and testing is performed in a consistent development environment—ensure compatibility at every step.
- Preserve modularity, testability, and robust error handling throughout.
- Each feature phase should be independently testable and deliver incremental value.

## API & Data Source Strategy (2025)

### Financials (SEC Filings/XBRL)
- **Primary:** [SEC EDGAR Full-Text Search API](https://www.sec.gov/edgar/sec-api-documentation) (free, official, robust)
- **Downloader:** [sec-edgar-downloader](https://github.com/jadchaar/sec-edgar-downloader) (Python, free, maintained)
- **XBRL Parsing:** [xbrlparse](https://github.com/greedo/python-xbrl) (lightweight, Python)
- **Backup:** [sec-api.io](https://sec-api.io/) (free tier, REST, easy for metadata/search, but rate-limited)

### Market Data (Stock Prices)
- **Primary:** [yfinance](https://github.com/ranaroussi/yfinance) (Yahoo Finance, free, Python, widely used)
- **Backup:** [Alpha Vantage](https://www.alphavantage.co/) (free API key, rate-limited)
- **Alternative:** [Stooq](https://stooq.com/) (free, CSV download, for global tickers)

### News & Sentiment (for v2+)
- **Primary:** [NewsAPI.org](https://newsapi.org/) (free tier, broad coverage, REST)
- **Backup:** [Finviz](https://finviz.com/) (web scraping, free, for headlines)
- **Sentiment:** [vaderSentiment](https://github.com/cjhutto/vaderSentiment) (free, Python, financial news compatible), [textblob](https://textblob.readthedocs.io/en/dev/), or [HuggingFace Transformers](https://huggingface.co/models) (for advanced NLP, free tier)

### Industry & Maturity Benchmarks
- **Primary:** [WRDS](https://wrds-www.wharton.upenn.edu/) (academic, not free, but public summary data may be available)
- **Alternative:** [Compustat](https://www.spglobal.com/marketintelligence/en/solutions/compustat-research-insight) (not free, but some open datasets exist)
- **Free/Public:** Use published Altman Z-Score coefficients by industry from academic papers or open data repositories (document sources in APIS.md)

### General Principles
- Prefer official, free, and well-documented APIs/libraries.
- Use backup sources for redundancy and validation.
- Document all API usage, rate limits, and licensing in APIS.md.
- Avoid paid APIs unless absolutely necessary for critical features.

## Updated Entry Point
- The main entry point for the Altman Z-Score analysis pipeline has been updated to `altman_zscore.py`.
- All references to `one_stock_analysis.py` in the documentation and examples have been updated accordingly.
- Ensure that the new entry point is tested and validated for all supported tickers.
