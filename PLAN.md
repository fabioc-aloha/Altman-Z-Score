# Vision: Exceeding the Competition

Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

> See [vision.md](./vision.md) for the full vision statement. Do not include the vision in other documentation.

# PLAN.md — Altman Z-Score Analysis Project

## Current Version: v3.0.0 (2025-06-07) ✅ FULLY COMPLETED

### Completed Modularization Milestone
- **✅ Full modular reorganization:** All code grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- **✅ All imports fixed:** Updated to use new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`)
- **✅ Integration testing:** Added `tests/test_integration_main.py` to catch import/runtime errors in main pipeline
- **✅ Critical import fixes:** Resolved all ModuleNotFoundError issues across the codebase:
  - Fixed `fetcher_factory.py`: `..company_profile` → `..company.company_profile`
  - Fixed `industry_classifier.py`: `.company_profile` → `..company.company_profile`
  - Fixed import paths in `output_generation.py`, `reporting.py`, `file_operations.py`, etc.
- **✅ Main pipeline verified:** Successfully runs `python main.py msft` without import errors
- **✅ Improved LLM prompt templates:** Enhanced code injection for reporting with more complete, context-aware analysis
- **✅ Documentation updated:** All documentation reflects new structure and completed modularization
- **✅ All tests passing:** Both unit tests and integration tests pass after reorganization
- **✅ Cleaned up obsolete files:** Removed duplicate files marked with 'D' in VS Code after reorganization
- **✅ Modularization & refactoring complete:** All refactoring work finished and fully tested

**🎯 v3.0.0 is now ready for production deployment and user feedback collection.**

---

## Development History & Key Achievements

### Major Project Milestones
- **v3.0.0 (2025-06-07):** Complete modularization, directory restructuring, and import path fixes - fully tested and production-ready
- **v2.8.x (2025-06-04):** Modularization of core files, improved error handling, comprehensive tests
- **v2.7.x (2025-06-03):** Major plotting refactoring, SEC EDGAR fallback implementation, improved error reporting 
- **v2.6.x:** Z-Score forecasting, sentiment/news analysis, multi-ticker portfolio support

### Core System Features
- **Data Fetching:** Multi-source data retrieval from Yahoo Finance, SEC EDGAR, and Finnhub
- **Model Selection:** Hierarchical decision tree for Z-Score model selection based on company characteristics
- **Validation:** Robust error handling, data consistency checks, and fallback mechanisms
- **Computation:** Flexible Z-Score calculation with multiple model support
- **Reporting:** Comprehensive analysis reports with qualitative validation and market context
- **Visualization:** Interactive and static plotting with trend analysis

## Next Steps (v3.1 Planning)

### Practical Use & User Feedback (Current Phase)
- Production deployment of v3.0.0 for real-world testing and feedback collection
- Monitor performance and identify any pain points in the modular structure
- Document insights from practical usage in LEARNINGS.md
- Draft v3.1 roadmap based on user feedback and operational insights

### Future Development Priorities

#### High Priority Improvements
- Advanced error handling for edge cases discovered in production
- Performance optimization based on real-world usage patterns
- Enhanced caching strategies to reduce API calls and improve response times

#### User Experience Enhancements
- Interactive dashboard for real-time analysis
- Enhanced CLI with additional command options and interactive mode
- Export format extensions (Excel, PowerBI, PDF)
- Custom notification system for Z-Score threshold alerts

#### Data & Analysis Extensions
- Currency conversion for non-USD firms
- "What-if" scenario analysis for financial planning
- Advanced forecasting using consensus estimates
- Industry-specific model calibration refinements

#### Integration & API Development
- REST API for programmatic access
- Database backend for historical data storage
- Third-party tool integrations
- Excel Add-In development

## Project Architecture & Implementation Principles

### Core Architecture
1. **Input Layer:** Accepts ticker(s) and analysis date; validates input
2. **Data Fetching Layer:** Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance, Finnhub)
3. **Validation Layer:** Validates raw data using Pydantic schemas; reports missing/invalid fields
4. **Computation Layer:** Computes Altman Z-Score using validated data; returns result object
5. **Reporting Layer:** Outputs results to CSV, JSON, or stdout; logs all steps and errors

### Implementation Principles
- **Simplicity:** Start with single-stock analysis, then generalize to portfolios
- **Modularity:** Clean separation of data fetching, validation, computation, and reporting
- **Testability:** Each module independently testable with clear interfaces
- **Robustness:** Strong error handling, logging, and data validation
- **Extensibility:** Easy to add new data sources, models, or output formats

### Development Philosophy
- Build robust MVPs before adding features
- Test thoroughly at each step
- Enable features incrementally with full testing and documentation
- Prioritize reliability and maintainability
- Follow conservative change management practices

## Technical Achievements & DRY Compliance

### Code Quality Improvements
- **Centralized Constants:** All field mappings, error messages, and configuration values defined in central locations
- **Unified Error Handling:** Standardized error classes and handling patterns across all modules
- **DRY-Compliant API Integration:** Consolidated data fetching logic for Yahoo Finance, SEC EDGAR, and Finnhub
- **Modular Components:** Clean functional separation with well-defined interfaces between modules
- **Comprehensive Testing:** Both unit tests and integration tests for all core functionality
- **Documentation Standards:** Consistent documentation style across all modules and APIs

### Key Technical Reference Files
- **Centralized Error Handling:** Standardized in `error_helpers.py`
- **Field Mapping Constants:** Defined in `computation/constants.py`
- **LLM Prompt Templates:** Stored in `src/prompts/`
- **API Endpoint Configuration:** Centralized in client classes (`sec_client.py`, `yahoo_client.py`, etc.)
- **Test Data & Fixtures:** Available in the `tests/` directory

### API Documentation
See `APIS.md` for detailed documentation of all external APIs used in this project, including:
- SEC EDGAR API for financial data
- Yahoo Finance API for market data
- Finnhub API for company profiles and logos
- LLM APIs for qualitative analysis

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
