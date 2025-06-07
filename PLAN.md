# Vision: Exceeding the Competition

Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

> See [vision.md](./vision.md) for the full vision statement. Do not include the vision in other documentation.

# PLAN.md — Altman Z-Score Analysis (v2.8.2)

## v2.8.2 Release (2025-06-04)
- Fixed critical issue with Z-Score report generation that caused duplicate content in reports
- Enhanced DataFrame handling in the reporting pipeline to prevent truthiness ambiguity errors
- Improved context data sanitization before passing to report generation functions
- Better error handling for data type conversions
- Fixed PEP 8 compliance for import statements in reporting module
- All tests passing, no breaking changes to APIs or outputs

## v2.8.0 Release (2025-06-04)
- Major refactor: full modularization of all core files and helpers
- All large files split into logical modules; all long functions decomposed into helpers
- Imports and references updated throughout
- Comprehensive tests for all modules; all outputs and APIs remain stable
- Documentation and usage examples updated to reflect new structure
- No breaking changes; all outputs and APIs remain stable

## v2.9.0 Release (2025-06-07)
- Full modular reorganization: all Python files grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- All imports updated to use new modular paths (e.g., from altman_zscore.plotting.plotting_main import plot_zscore_trend)
- Documentation and usage examples updated to reflect new structure
- All tests passing after reorganization
- No breaking changes to APIs or outputs

---

## v2.7.4 Release (2025-06-03)
- Major plotting refactor: plotting.py split into helpers and terminal modules
- Full test coverage for plotting_helpers and plotting_terminal
- Improved error handling and modularity in plotting pipeline
- Updated documentation and version numbers for v2.7.4
- No breaking changes; all outputs and APIs remain stable

## Updated Plan: Accomplishments and Next Steps

### Accomplishments (v2.7.1):
- Robust fallback to SEC EDGAR for financials if yfinance fails
- Improved error reporting: pipeline now transparently reports when only balance sheet data is available (e.g., TUP), and no Z-Score can be computed due to missing income statement data
- Documentation and release process updated for new fallback and error handling features
- All major architectural and technical decisions for this release are documented here and in LEARNINGS.md

### Accomplishments (v2.6):
- Z-Score forecasting using consensus estimates and/or time series models
- Sentiment and news analysis integration
- Generalized pipeline for multiple tickers and portfolio analysis
- Modularized data connectors and enhanced CLI for batch/portfolio analysis
- Prepared for web dashboard, REST API, and Excel Add-In
- Implemented advanced notifications for Z-Score thresholds
- Expanded tests and documentation for new features
- Reviewed user feedback and bug reports from v2.6
- Implemented improvements to LLM prompts and mapping logic based on feedback

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

## Planning for v2.7
- Collect and prioritize user feedback from v2.6
- Draft v2.7 roadmap (feature candidates: further LLM prompt tuning, additional data sources, advanced analytics, UI/UX improvements, etc.)
- Continue to modularize and document new features
- Expand integration and regression tests for new logic

## Architectural/Technical Decisions (v2.7)
- The data fetching layer now robustly falls back to SEC EDGAR if yfinance fails to provide financials.
- If only balance sheet data is available from SEC EDGAR, the pipeline will not attempt to compute a Z-Score and will transparently report this limitation to the user in the output and logs.
- Error messages for missing or partial financials are now propagated to the reporting layer for full transparency.

# --- 
# All pre-release and tested companies checklist items are now tracked in RELEASE_CHECKLIST.md. See that file for required actions before every release.

# DRY Improvement Plan (June 2025)

## Checklist: Eliminate Duplication and Centralize Logic

- [x] Centralize KNOWN_BANKRUPTCIES in company_status_helpers.py (done)
- [x] Centralize BANKRUPTCY_INDICATORS in company_status_helpers.py and import where needed
- [x] Ensure all field mapping constants (FIELD_MAPPING, MODEL_FIELDS) are defined in computation/constants.py and imported everywhere else
    - All references to FIELD_MAPPING and MODEL_FIELDS now import from computation/constants.py. No duplicate definitions remain in the codebase. See data_fetching/financials.py and financials_core.py for usage.
- [x] Centralize SEC EDGAR endpoint string as a constant or helper function
    - All SEC EDGAR endpoint URLs are now defined as constants in SECClient (api/sec_client.py) and imported everywhere else. No hardcoded SEC URLs remain in the codebase.
- [x] Centralize common error message strings as constants
    - All error message strings are now defined in computation/constants.py and imported everywhere else. No duplicate or hardcoded error messages remain in the codebase. See company_status_helpers.py and data_validation.py for usage.
- [x] Centralize yfinance data fetching/validation logic in a helper function
    - All yfinance data fetching and validation is now handled by fetch_yfinance_data and fetch_yfinance_full in api/yahoo_helpers.py. All usages in company_status_helpers.py and data_fetching/financials.py now use these helpers. No duplicate yfinance logic remains.
- [x] Ensure all delisting/bankruptcy/inactive checks are only in company_status_helpers.py
    - All status checks for delisting, bankruptcy, and inactive companies are now routed through check_company_status and handle_special_status in company_status_helpers.py. The main analysis pipeline in one_stock_analysis.py now uses these helpers, and no duplicate or stray logic remains elsewhere.
- [x] Review and centralize status message logic in CompanyStatus class
    - All user-facing status message templates are now defined as constants in computation/constants.py and used in CompanyStatus.get_status_message. No hardcoded status messages remain in the class.
- [x] Centralize output/report file naming and DataFrame-to-file logic (CSV/JSON) in utils/io.py; refactor all usages in one_stock_analysis.py, data_fetching/prices.py, fetch_prices.py, and company_status_helpers.py to use these helpers. (2025-06-04: All direct usages in these modules now refactored; DRY compliance achieved for output logic.)
- [x] Centralize logging setup and terminal output formatting (info, warning, error, header, etc.) in utils/logging.py and utils/terminal.py; refactor modules to use these helpers. (2025-06-04: Centralized logging and terminal output helpers created and adopted in fetch_prices.py. Validated for SONO and MSFT.)
- [x] Centralize model/field synonyms (e.g., mapping of alternate field names to canonical names) for DRY compliance in computation/constants.py or a dedicated synonyms module. Refactor all usages to import from this central location. (2025-06-04: FIELD_SYNONYMS now in computation/constants.py and used in financials_core.py for all synonym resolution.)
- [x] Centralize LLM prompt templates (e.g., field mapping, financial analysis) in src/prompts/ and ensure all code references these files for DRY compliance. (2025-06-04: All prompt templates are now stored in src/prompts/ and referenced from there.)
- [x] Centralize exception/error handling patterns (e.g., error message templates, error logging, and exception raising) in computation/constants.py and/or a dedicated error_helpers.py. Refactor modules to use these patterns for DRY compliance. (2025-06-04: error_helpers.py created; all custom exceptions now inherit from AltmanZScoreError; data_fetching/financials.py and api/sec_client.py refactored to use DRY error helpers. No stray exception logic remains.)

---

- Review and check off each item as it is completed
- Update this plan as new DRY opportunities are discovered or completed
