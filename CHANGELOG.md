# Changelog

All notable changes to the Altman Z-Score Analysis Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
