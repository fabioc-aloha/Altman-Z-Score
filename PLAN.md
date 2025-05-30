# PLAN.md — Altman Z-Score Analysis (v2.2.1)

## Version 2.2.1 (May 29, 2025)
- Centralized all LLM prompt files in `src/prompts/` and made them user-editable.
- Refactored prompt ingestion logic for robust path handling and runtime updates.
- Updated documentation (`README.md`, `PLAN.md`, `TODO.md`) to describe the new prompt workflow, folder structure, and version 2.2.1.
- Added a test checklist for prompt ingestion.
- Fixed bugs with prompt path logic and yfinance/pandas warnings.
- Moved chart image/caption before the LLM analysis in the report and into its own section.
- Made the LLM generate all section names, including references and disclaimers, per prompt instructions.
- Removed all hardcoded references, disclaimers, and section headings from the code.
- Improved terminal output to only show save status, not report content.
- Updated the financial analysis prompt to require a disclaimer, references, context-aware stakeholder tables, and to include source attribution and author.
- Updated the field mapping prompt to instruct the LLM to use semantic similarity/context, not just string matching.
- Removed the DOCX/Word export feature and all related code/docs.
- Added a hardcoded introduction, source attribution, author, and license to the top of the report in `reporting.py`.
- Made the source attribution and project/author reference consistent in both the prompt and the report.
- Removed the "Missing" column from the Raw Data Field Mapping Table in the report generator.
- Ensured the introduction and attribution are always at the very top of the generated report file and included in the LLM context.
- Added a developer disclaimer to the introduction.
- Updated the LICENSE to a custom "Attribution Non-Commercial License (MIT-based)" and referenced it in the report introduction.
- Moved the report title to the very top of the report, before the introduction, with correct line spacing.
- Fixed the report generator to ensure only one introduction section appears, immediately after the title, and not duplicated.
- Renamed the section "Analysis Context and Decisions" to "Analysis Context and Z-Score Model Selection Criteria".
- Staged, committed, and pushed changes to the main branch, including updated reports and documentation.
- Updated the version to 2.2.1 in all documentation and changelogs.

## Prompt Folder Usage
- All LLM prompt files are in `src/prompts/`.
- To customize LLM behavior, edit the relevant prompt file. Changes are reflected immediately in all outputs.
- For new LLM-driven features, add a new prompt file in `src/prompts/` and reference it in your code.

# Altman Z-Score Refactor Plan (2025, Revised)

## V2.2: Model Selection & Calibration Overhaul (May 2025, In Progress)
- Implements all recommendations from `altmans.md`:
  - Centralize all model coefficients, thresholds, and metadata in `constants.py` (with version/date/source fields).
  - Refactor company profile to include founding year, IPO date, and robust maturity classification.
  - Model selection logic uses age, IPO, industry (SIC), public/private status, and region.
  - Support for industry-specific and emerging market (EM) models and thresholds.
  - Reporting layer logs all model/threshold overrides, assumptions, and rationale.
  - Warnings for size/leverage outliers.
  - Document and automate calibration update process.
- See `altmans.md` for detailed requirements and rationale.
- **Implementation Steps:**
  1. Refactor `constants.py` to include all coefficients, thresholds, and metadata.
  2. Update company profile for founding year, IPO date, and maturity logic.
  3. Refactor model selection logic for new criteria.
  4. Enhance reporting for transparency and outlier warnings.
  5. Expand tests for new logic and edge cases.
  6. Document calibration update process in `altmans.md`.
  7. Integrate additional industry benchmark data as available.
  8. Schedule periodic calibration updates.

## V2.0.1 Release: Bug Fix and Resilience Improvement (May 28, 2025)

- **Release V2.0.1** focuses on bug fixes, output folder/file handling, and improved resilience:
  - All output file and directory creation is now fully centralized and robust (no hardcoded paths).
  - If a ticker is invalid or unavailable, a clear marker file (`TICKER_NOT_AVAILABLE.txt`) is written in the output folder, and no other files are created.
  - Removed all legacy, redundant, or confusing output files (component tables, summary, profile, etc.).
  - Documentation and code comments have been updated for clarity and maintainability.
  - The codebase is now more robust to edge cases and easier to maintain.

---

## May 2025 Update

- **V2 is complete and merged to main.**
- All outputs are now per-ticker, the main entry point is main.py, and the codebase is free of deprecated files.
- See below for the V2.5 roadmap (forecasting, sentiment, portfolio analysis).

---

## Version Milestones
- **V2.2 (Current):**
  - Model selection & calibration overhaul with enhanced visualizations
  - Improved plotting with I-shaped whiskers, better label positioning, and optimized scaling
  - Example output reports for MSFT, RIVN, SONO, and TSLA
- **V2.1:**
  - Stable Z-Score trend analysis, robust reporting, per-ticker outputs, and codebase cleanup.
  - All outputs are per-ticker, main entry point is main.py, and deprecated files are removed.
- **V2.2: Model Selection & Calibration (May 2025):**
  - Model selection now uses company age, IPO date, industry (SIC), public/private status, and region.
  - Maturity is classified as early-stage, growth, or mature using founding year and IPO date.
  - All model coefficients and thresholds are centralized in `src/altman_zscore/computation/constants.py`.
  - Industry-specific and emerging market (EM) models are supported.
  - The reporting layer logs all model/threshold overrides and lists assumptions and rationale.
  - Warnings are included for size/leverage outliers.
  - The architecture is fully extensible for new models and calibration updates.
  - See `altmans.md` for the detailed implementation plan and calibration process.
- **V2.5: Z-Score Forecasting, Sentiment, and Plotting Enhancements**
- **V2.6: Portfolio/multi-ticker analysis**
- **V2.7: Advanced correlation and insights**
- **V2.8: Community contributions and plugin support**

---

## V2.5 Roadmap: Forecasting, Sentiment, and Portfolio Analysis
- **Forecasting:**
  - Add the ability to forecast the next quarter's Z-Score using consensus estimates and/or time series models.
  - Integrate APIs for consensus estimates (Yahoo Finance, others).
  - Design a lightweight, explainable forecasting model.
  - Display forecasted Z-Score alongside historical trends in reports and plots.
- **Sentiment & News Analysis:**
  - Integrate news and sentiment APIs (e.g., NewsAPI, Finviz, vaderSentiment).
  - Correlate news/sentiment with Z-Score and price trends.
  - Add news/sentiment highlights to the full report.
- **Portfolio/Multi-Ticker Analysis:**
  - Generalize the pipeline to accept and process multiple tickers in a single run.
  - Output per-ticker results and aggregate/portfolio-level summaries.
  - Add CLI and reporting support for batch/portfolio analysis.
- **Testing & Documentation:**
  - Add/expand tests for new v2.5 features.
  - Update documentation (README, PLAN.md, etc.) for v2.5 features and usage.
  - Ensure all v2 features remain stable and well-tested during v2.5 development.

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
   - Write a pure function `compute_zscore(validated_data, industry, maturity)` .
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
- [x] **v2: Enhanced Reporting (Full report file generation)**
  - [x] Comprehensive, well-formatted report saved as `output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt`
  - [x] Includes context, field mapping, Z-Score component table with risk area diagnostics, and all formulas
  - [x] **v2.1: Granular Stock Price Analysis**
  - [x] Introduce monthly granularity for stock price trends in the chart.
  - [x] Add whisker/error bars to represent price ranges (e.g., high/low prices for each month).
  - [x] Generate a detailed stock price data file for future analysis, saved as `output/<TICKER>/monthly_prices.csv` and `output/<TICKER>/monthly_prices.json`.
- [ ] **v2.5: Z-Score Forecasting & Sentiment Analysis**
  - [ ] **Z-Score Forecasting Feature:**
    - Fetch consensus estimates for key financial metrics (e.g., revenue, EBITDA, net income) from Yahoo Finance or other APIs.
    - Develop a lightweight forecasting model to estimate Z-Score components based on collected data.
    - Extend the computation layer to include forecasted Z-Score values.
    - Update the reporting layer to display forecasted Z-Score alongside historical trends.
  - [ ] **Sentiment Analysis Feature:**
    - Integrate sentiment analysis and news highlights
    - Correlate operational health from news/SEC filings with Z-Score and price
- [ ] **v3: Portfolio Analysis**
  - Generalizes pipeline to handle multiple tickers, batch analysis, and reporting
- [ ] **v4: Advanced Correlation & Insights**
  - Correlates Z-Score, price, and operational health metrics
  - Generates insights and alerts

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
- The main entry point for the Altman Z-Score analysis pipeline has been updated to `main.py` in the project root (formerly `altman_zscore.py`).
- All references to `one_stock_analysis.py` in the documentation and examples have been updated accordingly.
- All outputs are now organized by ticker in `output/<TICKER>/`.
- Ensure that the new entry point is tested and validated for all supported tickers.

## Qualitative Validation & News Integration (v2+)

- Each Z-Score report now includes an LLM-generated qualitative validation section.
- This section provides:
  - A concise summary contextualizing the Z-Score result (e.g., "Safe Zone", "Distress Zone")
  - 2-3 recent news headlines with links (Markdown format)
  - Explicit references to credit ratings, analyst reports, and news sources
- The prompt template for the LLM explicitly requests news headlines with links and reference lists.
- This approach ensures every report is actionable, reference-backed, and easy to audit.
- The platform is now ready for further sentiment analysis, news/sentiment trend charts, and portfolio-level analytics in future versions.

---

## Plotting and Visualization Improvements (May 29, 2025)
- **Enhanced Z-Score and Stock Price Visualizations:** 
  - ✅ Improved label positioning with Z-Score values above markers and price values above their points
  - ✅ Implemented I-shaped whiskers with horizontal caps for price range indicators
  - ✅ Optimized y-axis scaling to prevent overlapping between Z-Score and price data
  - ✅ Enhanced color scheme with darker gray for price axis and better readability
  - ✅ Fixed indentation issues in plotting code with consistent 4-space indentation
  - ✅ Added responsive margins to both axes to accommodate different data ranges
  - ✅ Added proper parameter names in annotate functions for better code quality
- **Example Reports:**
  - ✅ Added example output reports to the repository for demonstration purposes
  - ✅ Updated README.md with "Output Examples" section explaining the included reports
  - ✅ All examples now show properly formatted Z-Score trend analysis with price overlay

## Prompt Ingestion for LLM Analysis (May 2025)

- All LLM prompt files are now stored in `src/prompts/` for clarity and maintainability.
- The pipeline reads these files at runtime and combines them with the current report context before sending to the LLM.
- Any changes to these prompt files are immediately reflected in all future reports—no code changes required.
- This enables full transparency, reproducibility, and user control over the LLM's analysis style, instructions, and references.
- See `README.md` for user instructions and workflow.

---

## Change Log: DOCX/Word Export Removal (May 29, 2025)
- The DOCX/Word export feature has been removed from the codebase due to persistent formatting and chart embedding issues.
- All documentation and code references to DOCX/Word export have been removed.
- Reports are now generated in Markdown format only.

### Rationale
- The DOCX export feature did not meet professional standards for formatting and chart/image embedding.
- Markdown output remains robust, portable, and easy to convert to other formats if needed.

### Next Steps
- If high-quality Word export is required in the future, consider using a dedicated Markdown-to-Word tool or service outside this codebase.

# PLAN: Field Mapping and Internationalization Improvements (May 2025)

## Objective
Enhance the Altman Z-Score pipeline's field mapping, internationalization, and robustness for global and emerging market tickers, with a focus on banks/financials and user transparency.

---

## 1. Expand FIELD_SYNONYMS
- Add more synonyms for each canonical field, especially for banks and international companies (Portuguese, Spanish, French, etc.).
- Include terms like "Receita de Juros" (Interest Income), "Lucro Líquido" (Net Income), etc.

## 2. Bank/Financial Institution Awareness
- Detect if a company is a bank/financial institution (from sector/industry or ticker list).
- Adjust mapping priorities for banks (e.g., map 'sales' to 'Interest Income' if no revenue field is present).

## 3. Partial/Fallback Mapping Reporting
- When a field cannot be mapped, include a 'Reason' in the returned mapping (e.g., 'No revenue field found; company may be a bank').
- Surface this in the report for transparency.

## 4. Sample Value Matching
- Use sample_values (if provided) to improve mapping confidence (e.g., match by value type/range).

## 5. Case-Insensitive and Accent-Insensitive Matching
- Normalize field names (lowercase, remove accents/diacritics) before matching.

## 6. Logging and Diagnostics
- Add granular logging for mapping decisions, especially for fallbacks and unmapped fields.

## 7. User-Editable Mapping Overrides
- Allow user to provide a mapping override file (e.g., mapping_overrides.json) for persistent issues.

## 8. Unit Tests for Mapping Logic
- Add/expand unit tests for edge cases, especially for international tickers and banks.

## 9. Graceful Handling of LLM Failures
- If LLM response is malformed/missing, fall back to code-level synonym matching and log a warning.

## 10. Documentation
- Document mapping logic, fallback rules, and internationalization in README or a dedicated doc.

---

## Next Steps
- Prioritize FIELD_SYNONYMS expansion and bank awareness logic.
- Implement fallback reporting and logging.
- Add user-editable mapping override support.
- Update tests and documentation.
