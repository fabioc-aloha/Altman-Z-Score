# Vision: Exceeding the Competition

Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

> See [vision.md](./vision.md) for the full vision statement. Do not include the vision in other documentation.

# PLAN.md — Altman Z-Score Analysis (v2.5)

## Updated Plan: Accomplishments and Next Steps

### Accomplishments:
- **Data Fetching Enhancements:**
  - Integrated additional data fetching from `yfinance`, including historical prices, dividends, and stock splits.
  - Fetched and saved `company_info`, `major_holders`, `institutional_holders`, and `recommendations` from `yfinance`.
  - Implemented a function `fetch_sec_edgar_data` to fetch company information from SEC EDGAR.
  - Ensured all JSON files saved in the output directory are pretty-formatted.

- **Model Selection and Z-Score Computation:**
  - Hierarchical decision tree for Z-Score model selection based on SIC, Emerging Market flag, and Public/Private maturity.
  - Centralized configuration for model coefficients, intercepts, and thresholds.
  - Validation of required fields and accounting identities.
  - Ratio range checks and consistency warnings.
  - Computation dispatcher for Z-Score calculation and diagnostic assignment.

- **Qualitative Validation:**
  - Designed a prompt template summarizing company details, Z-Score, and financial highlights.
  - Integrated LLM call to generate qualitative validation.
  - Appended qualitative validation section to `zscore_full_report` with LLM summary, news headlines, and references.
  - Error handling for LLM call failures with fallback messaging.
  - Tested on multiple tickers to ensure relevance and accuracy of LLM output.
  - Documented the qualitative validation feature in `README.md` and `PLAN.md`.

### Pending:
- **Validation and Error Handling:**
  - Validate the accuracy and usefulness of SEC EDGAR data.
  - Improve error handling for both `yfinance` and SEC EDGAR data fetching.
  - Enhance identity checks to catch inter-quarter restatements and detect stale XBRL contexts.

- **Pipeline Refinements:**
  - Finalize and implement the checklist in `DataFetching.mp`.
  - Caching of LLM responses for auditability and cost control.
  - Advanced notifications for Z-Score thresholds.
  - Refinement of prompt and output formatting based on user feedback.

- **Future Features:**
  - Currency conversion for non-USD firms.
  - "What-if" scenario analysis for CAPEX adjustments.
  - Integration of RACI chart for execution ownership.
  - Optimization of data caching to reduce API calls.
  - Forecasting next quarter's Z-Score using consensus estimates and/or time series models.
  - Sentiment and news analysis integration.
  - Generalization of pipeline for multiple tickers and portfolio analysis.

---

## Short-Term Action Items (for TODO.md)
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
- Begin v2.5: Z-Score forecasting, sentiment/news analysis, and multi-ticker/portfolio support

## Current Version: v2.4 (May 30, 2025)
- Weekly-only simplification, CLI/pipeline/docs/tests updated, dispatcher/model logic improved
- All plotting and reporting logic updated for weekly-only data
- All documentation and tests updated for weekly-only support

## v2.5 Roadmap: Portfolio Analysis and Modularization
- Portfolio/Multi-Ticker Analysis: Generalize pipeline for multiple tickers, output per-ticker and aggregate summaries
- Testing & Documentation: Add/expand tests for new v2.5 features, update documentation for v2.5 features and usage

## Planned/Future Features
- Forecasting: Add ability to forecast next quarter's Z-Score using consensus estimates and/or time series models
- Sentiment & News Analysis: Integrate news and sentiment APIs, correlate with Z-Score and price trends

## Implementation Principles
- Simplicity: Start with a single-stock analysis pipeline, then generalize to portfolios
- Modularity: Clean separation of data fetching, validation, computation, and reporting
- Testability: Each module is independently testable with clear interfaces
- Robustness: Strong error handling, logging, and data validation at every step
- Extensibility: Easy to add new data sources, models, or output formats

## Architecture Overview
1. Input Layer: Accepts ticker(s) and analysis date; validates input
2. Data Fetching Layer: Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance)
3. Validation Layer: Validates raw data using Pydantic schemas; reports missing/invalid fields
4. Computation Layer: Computes Altman Z-Score using validated data; returns result object
5. Reporting Layer: Outputs results to CSV, JSON, or stdout; logs all steps and errors

## Conservative, Incremental Rollout Policy
- Build a minimal, robust MVP first (single-stock Z-Score trend analysis)
- Test thoroughly at each step before enabling new features
- Only enable new features after the MVP is stable and well-tested
- Light up features one at a time, with tests and documentation, to avoid regressions
- Avoid over-ambitious changes; prioritize reliability and maintainability

## Roadmap: Prioritized Ideas by Complexity

### High Priority, Low Complexity
1. **Validation and Error Handling:**
   - Validate the accuracy and usefulness of SEC EDGAR data.
   - Improve error handling for both `yfinance` and SEC EDGAR data fetching.
   - Enhance identity checks to catch inter-quarter restatements and detect stale XBRL contexts.

2. **Pipeline Refinements:**
   - Finalize and implement the checklist in `DataFetching.mp`.
   - Refine prompt and output formatting based on user feedback.

3. **Documentation and Testing:**
   - Expand unit/integration tests for new model selection and reporting logic.
   - Improve documentation for mapping, prompt usage, and internationalization.

---

### High Priority, High Complexity
1. **Future Features:**
   - Forecasting next quarter's Z-Score using consensus estimates and/or time series models.
   - Sentiment and news analysis integration.
   - Generalization of pipeline for multiple tickers and portfolio analysis.

2. **Advanced Notifications:**
   - Implement advanced notifications for Z-Score thresholds.

---

### Medium Priority, Medium Complexity
1. **Qualitative Validation Enhancements:**
   - Caching of LLM responses for auditability and cost control.
   - "What-if" scenario analysis for CAPEX adjustments.

2. **Data Infrastructure:**
   - Currency conversion for non-USD firms.
   - Integration of RACI chart for execution ownership.
   - Optimization of data caching to reduce API calls.

---

### Long-Term Goals
1. **Web Dashboard and API:**
   - Prepare for web dashboard, REST API, and Excel Add-In.

2. **AI and Machine Learning:**
   - Experiment with ML models for future Z-Score predictions.
   - Add AI-powered anomaly detection for ratio trends.

3. **Industry Benchmarking:**
   - Integrate additional industry benchmark data (WRDS/Compustat or open data) into constants.py.

---

# ---
# All pre-release and tested companies checklist items are now tracked in RELEASE_CHECKLIST.md. See that file for required actions before every release.
