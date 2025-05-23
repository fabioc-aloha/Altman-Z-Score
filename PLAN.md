# Altman Z-Score Refactor Plan (2025, Revised)

## Background
This plan is based on the new concept outlined in `OneStockAnalysis.md` and incorporates learnings from the previous codebase (now in `OLD/`). The goal is to create a robust, modular, and testable Altman Z-Score analysis tool for single stocks and portfolios, with a focus on reliability, data integrity, and ease of maintenance.

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
   - Parses XBRL using `arelle` or `xbrlparse` (latest maintained).
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
   - Use only minimal, modern dependencies (`pandas`, `requests`, `pydantic`, `yfinance`, `sec-api`, `arelle`/`xbrlparse`, `matplotlib`/`plotly`).
2. **Implement Input & Config Handling**
   - Parse CLI args or function params for ticker, date, industry, and maturity.
   - Validate inputs.
3. **Implement Data Fetching**
   - Write `fetch_sec_financials(ticker, date)` using `sec-api` or `sec-edgar-downloader`.
   - Parse XBRL with `arelle` or `xbrlparse`.
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
  - Outputs Z-Score trend as table and plot
- [ ] **v1: Overlay Stock Price Trend**
  - Fetches and overlays stock price trend for the same period
  - Combined plot of Z-Score and price
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
- All development and testing is performed in GitHub Codespaces—ensure compatibility at every step.
- Preserve modularity, testability, and robust error handling throughout.
- Each feature phase should be independently testable and deliver incremental value.

## API & Data Source Strategy (2025)

### Financials (SEC Filings/XBRL)
- **Primary:** [SEC EDGAR Full-Text Search API](https://www.sec.gov/edgar/sec-api-documentation) (free, official, robust)
- **Downloader:** [sec-edgar-downloader](https://github.com/jadchaar/sec-edgar-downloader) (Python, free, maintained)
- **XBRL Parsing:** [arelle](https://arelle.org/) (open-source, industry standard, supports US-GAAP/IFRS), or [xbrlparse](https://github.com/greedo/python-xbrl) (lightweight, Python)
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
- **Free/Public:** Use published Altman Z-Score coefficients by industry from academic papers or open data repositories (document sources in DECISIONS.md)

### General Principles
- Prefer official, free, and well-documented APIs/libraries.
- Use backup sources for redundancy and validation.
- Document all API usage, rate limits, and licensing in DECISIONS.md.
- Avoid paid APIs unless absolutely necessary for critical features.

---

**Next Action:**
- Begin implementation at `src/altman_zscore/one_stock_analysis.py` following this plan, using the latest libraries and calibration techniques.

## Archival of Previous Version
- The entire previous codebase (code, scripts, tests, docs) is now in the `OLD/` directory for reference and rollback.
- See `OLD/README.md` for details on the archived structure and usage policy.
