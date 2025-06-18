# Changelog

All notable changes to the Altman Z-Score Analysis Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.2] - 2025-06-17

### Added
- **Actionable README Table:** New "Investor Advice" column in portfolio table
  - Automatically extracts investment recommendations from each company's Z-Score report
  - Displays clear, emoji-coded advice: 📈 BUY, ⚖️ HOLD, 📉 SELL, 📊 MIXED
  - Shows recommendation ratios (e.g., "BUY (4/6)") for transparency
  - Makes the README portfolio table immediately actionable for investors

### Enhanced
- **generate_readme_table.py:** Intelligent parsing of investor recommendation tables
  - Advanced regex patterns to extract recommendation summaries
  - Fallback logic to count individual recommendations when summary unavailable
  - Robust error handling for missing or malformed recommendation data
  - Support for various recommendation formats across different report styles

## [3.4.1] - 2025-06-17

### Changed
- **Documentation Enhancement:** Streamlined README with comprehensive portfolio explanation
- **Portfolio Organization:** Detailed breakdown of 39 companies across 5 strategic market segments
- **User Experience:** Improved documentation readability and portfolio value proposition
- **Educational Value:** Added clear explanations of why each company category was selected for testing

## [3.4.0] - 2025-06-17

### Added
- **Comprehensive Test Portfolio:** Added full analysis results for 39 diverse companies
  - **Large Cap Tech:** AAPL, MSFT, NVDA, GOOGL, GOOG, AMZN, META
  - **Growth/SaaS:** SNOW, PLTR, UBER, DDOG, DOCU, CRWD, NET, MDB, SHOP, ROKU, RBLX, ZM
  - **Financial Services:** JPM, COIN, AFRM
  - **Distressed/Cyclical:** AAL, UAL, AMC, CCL, F, GE, GME, T
  - **Established Companies:** JNJ, PG, KO, UNH, VZ, WMT, CAT, DUK, ADP, SLB
  - Updated README.md with comprehensive table showing all 39 analyzed companies  - All companies include full LLM reports, trend charts, and company logos

### Changed
- **README Enhancement:** Streamlined documentation with detailed portfolio composition breakdown
- **Portfolio Organization:** Companies categorized by market segment and financial profile  
- **Documentation Structure:** Improved readability with clear sections explaining portfolio value and testing coverage
- **CLI Interface Improvement:** Renamed `--start` argument to `--date` for better usability
  - Changed CLI argument from `--start` to `--date` to make the purpose more intuitive
  - Updated help text: "Analysis date for historical data" instead of "Start date for analysis"
  - All validation and functionality remains identical - only the argument name changed
  - **Breaking Change**: Users must now use `--date` instead of `--start`

### Fixed
- **Critical Report Generation Bug:** Fixed LLM report generation regression
  - Resolved typo in `src/altman_zscore/core/output_generation.py` (line 35: `toDict` → `to_dict`)
  - Fixed indentation errors in report generation pipeline
  - All tickers now generate complete `zscore_TICKER_zscore_full_report.md` files
- **Code Formatting:** Fixed multiple formatting issues in main.py argument parser
  - Corrected missing newlines between argument definitions
  - Fixed indentation issues in function definitions
  - Improved code readability and maintainability

### Documentation
- Updated README.md with new `--date` argument examples
- Updated FLOW.md with correct CLI usage patterns
- Updated PowerShell scripts and copilot documentation files
- Updated all documentation files to reflect the new argument name
- Comprehensive version bump to 3.4.0 across all files

## [3.3.4] - 2025-06-17

### Changed
- **CLI Interface Improvement:** Renamed `--start` argument to `--date` for better usability
  - Changed CLI argument from `--start` to `--date` to make the purpose more intuitive
  - Updated help text: "Analysis date for historical data" instead of "Start date for analysis"
  - Updated all usage examples in documentation and code comments
  - Backward compatibility note: Users must now use `--date` instead of `--start`
  - All validation and functionality remains identical - only the argument name changed

### Fixed
- **Code Formatting:** Fixed multiple formatting issues in main.py argument parser
  - Corrected missing newlines between argument definitions
  - Fixed indentation issues in function definitions
  - Improved code readability and maintainability

### Documentation
- Updated README.md with new `--date` argument examples
- Updated FLOW.md with correct CLI usage patterns
- Updated all documentation files to reflect the new argument name

## [3.3.3] - 2025-06-17

### Fixed
- **Major UX Improvement:** Eliminated confusing HTTP 401 error messages that appeared during normal API rate limiting
  - SEC API: 401 errors now handled gracefully with INFO-level logging instead of ERROR-level
  - Yahoo Finance API: Added specific 401 error detection and appropriate logging
  - Retry Decorator: Enhanced to detect and handle 401 errors with appropriate log levels
  - Pipeline now runs completely clean without alarming error messages for expected API rate limiting
  - All fallback mechanisms continue to work seamlessly
  - Improved user experience with professional, non-confusing output

## [3.3.2] - 2025-06-17

### Fixed
- **Major UX Improvement:** Eliminated confusing HTTP 401 error messages that appeared during normal API rate limiting
  - SEC API: 401 errors now handled gracefully with INFO-level logging instead of ERROR-level
  - Yahoo Finance API: Added specific 401 error detection and appropriate logging
  - Retry Decorator: Enhanced to detect 401 errors and log them as informational rather than errors
  - Pipeline continues seamlessly with fallback mechanisms while providing clean, professional output
- **User Experience:** Analysis now runs completely clean without alarming error messages for expected API limitations
- **Logging:** More informative and user-friendly messages that don't suggest system failures

### Technical Details
- Modified `src/altman_zscore/api/sec_client.py` to return None instead of raising exceptions for 401 errors
- Enhanced `src/altman_zscore/api/yahoo_helpers.py` with specific HTTP 401 error handling
- Updated `src/altman_zscore/utils/retry.py` to detect and appropriately log 401 errors
- All functionality preserved - only logging behavior improved for better user experience

## [3.3.0] - 2025-06-17

### Added
- **LLM Copilot Analysis Framework:** Complete integration for systematic pipeline output evaluation
  - Added `copilot.md` with comprehensive step-by-step instructions for LLM-driven troubleshooting
  - VS Code tool integration using list_dir, read_file, grep_search, run_in_terminal for analysis
  - Mandatory audit trail creation via `Copilot_Troubleshoot.md` before any code changes
  - Systematic workflow for ticker inventory, success rate assessment, and issue pattern detection
- **Deep Report Evaluation Preparation:** Enhanced framework for comprehensive output analysis
  - Success criteria definition for complete vs. incomplete ticker analysis
  - File completeness assessment tools and data quality validation workflows
  - Root cause analysis capabilities for common failure patterns
- **Model Matching Modernization Preparation:** Documentation and framework setup for model selection enhancement
  - Current model selection logic documented and analyzed
  - Framework prepared for intelligent model matching based on company characteristics

### Changed
- **Documentation Enhancement:** Updated README.md, FLOW.md, and TODO.md to reference new troubleshooting capabilities
- **Project Structure:** Added comprehensive troubleshooting documentation and analysis tools
- **Development Workflow:** Established systematic approach for pipeline analysis and debugging

### Fixed
- **Analysis Consistency:** Standardized troubleshooting approach ensures consistent issue investigation
- **Tool Integration:** Leveraged VS Code built-in capabilities for efficient debugging workflows

## [3.2.1] - 2025-06-17

### Fixed
- **Historical Data Coverage:** Fixed Z-Score calculation to include historical data back to user-specified start date
  - Modified `yahoo_helpers.py` to fetch both quarterly and annual financial data from yfinance
  - Updated `financials.py` to combine quarterly and annual data for comprehensive historical coverage
  - Extended Z-Score trend analysis from ~2 years to ~5 years of historical data
- **Import Errors:** Resolved undefined variable and import issues in core pipeline modules
  - Fixed `stock_prices` undefined variable in `plotting_main.py`
  - Corrected import paths for `check_company_status`, `sic_map`, and `FinancialMetrics`
  - Fixed function name mismatch (`calculate_zscore` vs `compute_zscore`)
- **Date Range Alignment:** Both price data and Z-Score data now properly honor user-specified start dates
- **Pipeline Robustness:** Enhanced error handling and data validation throughout the analysis pipeline

### Changed
- **Data Fetching Strategy:** Enhanced yfinance integration to use both quarterly (recent detail) and annual (historical coverage) financial statements
- **Chart Generation:** Z-Score trend charts now display comprehensive historical data aligned with stock price trends

## [3.2.0] - 2025-06-16

### Added
- **Enhanced Visualization:** 
  - Added improved candlestick representation in chart legends
  - Added company logo display in bottom-left corner of charts
- **Error Handling:** Added graceful continuation for multi-ticker analysis when one ticker fails

### Changed
- **Chart Improvements:** 
  - Better visual representation of weekly price range in legends
  - Clearer distinction between up/down candlesticks
  - Added company branding with logo integration
- **Error Handling:** More informative messages for missing financial data
- **Yahoo Finance Client:** Improved retry logic and error handling for API requests

### Fixed
- **Pipeline Robustness:** Improved handling of missing SEC data and failed ticker analysis
- **Legend Display:** Fixed candlestick legend representation to match chart style
- **API Authentication:** Enhanced Yahoo Finance client to handle authentication issues

## [3.1.1] - 2025-06-15

### Added
- **FLOW.md:** New documentation file describing the codebase architecture and flow
- **Updated output directory structure documentation:** More detailed information about output files and formats

### Changed
- **Improved documentation:** Better descriptions of file outputs and directory structure
- **Enhanced plotting:** Fixed minor issues with rendering charts
- **Data pipeline enhancements:** More robust handling of financial data from multiple sources

### Fixed
- **SEC EDGAR data processing:** Addressed edge cases in data reconciliation
- **Visualization alignment:** Fixed alignment issues in Z-Score trend charts

## [3.0.0] - 2025-06-07 ✅ FULLY COMPLETED

### Added
- **✅ Full modular reorganization:** All code grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- **✅ Integration testing:** Added `tests/test_integration_main.py` to catch import/runtime errors in main pipeline
- **✅ Critical import fixes:** Resolved all ModuleNotFoundError issues across the codebase

### Changed
- **✅ All imports updated:** Use new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`)
- **✅ Improved LLM prompt templates:** Enhanced code injection for reporting with more complete, context-aware, and robust analysis outputs
- **✅ Documentation updated:** All documentation reflects new structure and completed modularization

### Fixed
- **✅ Import errors:** Fixed critical import paths in `fetcher_factory.py`, `industry_classifier.py`, and other core modules
- **✅ Main pipeline:** Successfully runs `python main.py msft` without import errors
- **✅ Test collection:** Fixed pytest issues in `test_finnhub.py` by removing `sys.exit(1)` and renaming helper functions

### Technical
- **✅ All tests passing:** Both unit tests and integration tests pass after reorganization
- **✅ Cleaned up obsolete files:** Removed duplicate files marked with 'D' in VS Code after reorganization
- **✅ Main pipeline verified:** Integration testing confirms the modular structure works correctly
- **✅ Modularization & refactoring complete:** All refactoring work finished and fully tested

**🎯 v3.0.0 is now ready for production deployment and user feedback collection.**

## [2.9.0] - 2025-06-05

### Added/Changed
- Automated company logo download, resizing, and standardized naming in Finnhub API client and reporting pipeline.
- Markdown reports now include company logo at the top, with consistent sizing and file naming.
- Automated README sample reports table generation: logos, company names, report/chart links, and API credits/disclaimers are now dynamically generated for all tickers in `output/`.
- Added `generate_readme_table.py` script to automate README table updates.
- Updated release checklist for v2.9.0 and preserved previous release history.
- Updated version numbers in `README.md` and `main.py` to 2.9.0.

### Technical
- Improved modularity and error handling in logo and report generation logic.
- Ensured no redundant logo downloads or resizings; robust file existence checks.
- All automation scripts and reporting logic compatible with local and cloud environments.

### Breaking Changes
- None. All outputs and APIs remain stable.

## [2.8.6] - 2025-06-05

### Added/Changed
- CLI improvements: input validation, log level enforcement, default-to-help, exit code on failure, and robust logging throughout.
- Updated documentation and README to reflect new CLI features and architecture.
- Release checklist reset for 2.8.6 with focus on CLI enhancements.

## [2.8.2] - 2025-06-04

### Bug Fixes & Reporting Improvements
- Fixed critical issue with Z-Score report generation that caused duplicate content in reports
- Enhanced DataFrame handling in the reporting pipeline to prevent truthiness ambiguity errors
- Improved context data sanitization before passing to report generation functions
- Better error handling for various data type conversions
- Fixed PEP 8 compliance for import statements in reporting module

## [2.8.1] - 2025-06-04

### DRY Refactor & Release Checklist
- Major DRY refactor: centralized all error handling, constants, and logic in dedicated modules (see PLAN.md for details)
- All custom exceptions now inherit from AltmanZScoreError; error handling is fully DRY-compliant
- All error messages, status messages, and field mappings are now centralized
- All outputs, APIs, and tests remain stable
- Documentation and release checklist updated for v2.8.1

## [2.8.0] - 2025-06-04

### Major Refactor & Modularization
- Complete modularization of all major files: business logic, plotting, OpenAI, and company data now separated into dedicated helper modules.
- All large files (>300 lines) split into logical modules; all long functions (>50 lines) decomposed into helpers.
- Imports and references updated throughout the codebase.
- Comprehensive tests added/updated for all new/refactored modules; all tests pass and outputs validated.
- Documentation and usage examples updated to reflect new structure.
- No breaking changes; all outputs and APIs remain stable.

## [2.7.4] - 2025-06-03
- Major plotting refactor: plotting.py split into helpers and terminal modules
- Full test coverage for plotting_helpers and plotting_terminal
- Improved error handling and modularity in plotting pipeline
- Updated documentation and version numbers for v2.7.4
- No breaking changes; all outputs and APIs remain stable

## [2.7.3] - 2025-06-03

### Changed
- Codebase cleanup: removed dead code, verified all modules and prompt files are referenced and in use
- Updated documentation and version numbers for v2.7.3
- No breaking changes; all outputs and APIs remain stable

## [2.7.2] - 2025-06-03

### Documentation
- Verified and updated DataFetching.md with comprehensive checkmarks and implementation status
- Added RELEASE_CHECKLIST.md for reproducible release process
- Ensured all documentation files are consistent and up to date

### Technical
- No code changes; documentation and release process improvements only

## [2.7.1] - 2025-06-03

### Added
- Enhanced executive/officer information injection into LLM qualitative analysis
- Improved company profile data integration in reports
- Better error handling for missing officer data in LLM prompts

### Fixed
- Fixed issue with missing officer data in LLM prompts that could cause analysis failures
- Improved data validation for company officer information

### Changed
- Enhanced LLM commentary generation with more comprehensive executive data
- Updated prompts to better handle cases where officer information is unavailable

### Technical
- Improved error handling in `openai_client.py` for missing data scenarios
- Enhanced data fetching robustness in `sec_client.py`
- Updated reporting logic to gracefully handle incomplete officer data

## [2.7.0] - 2025-05-XX

### Added
- Multi-ticker portfolio analysis support
- Enhanced visualization with trend plotting
- Comprehensive financial metrics validation
- Industry-specific Z-Score model selection
- Executive officer data integration

### Enhanced
- Modular architecture with separate data fetching, computation, and reporting layers
- Robust error handling and logging throughout the pipeline
- Comprehensive data validation using Pydantic schemas

## [2.6.0] - 2025-04-XX

### Added
- SEC EDGAR data integration
- Advanced financial metrics computation
- Automated report generation
- Weekly price data analysis

## Earlier Versions

For changes in versions 2.5.0 and earlier, please refer to the git commit history and PLAN.md file.
