# Vision Alignment

All technical learnings and decisions in this document are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

# LEARNINGS.md — Altman Z-Score Analysis (v3.0.0)

## Version 3.0.0 (June 7, 2025) ✅ FULLY COMPLETED
- **✅ Full modular reorganization:** All code successfully grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- **✅ Import path fixes:** Updated all imports to use new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`)
- **✅ Critical import error resolution:** Fixed multiple import errors that occurred during reorganization:
  - `fetcher_factory.py`: Changed `..company_profile` to `..company.company_profile`
  - `industry_classifier.py`: Changed `.company_profile` to `..company.company_profile`
  - Fixed import paths in `output_generation.py`, `reporting.py`, `file_operations.py`, `one_stock_analysis.py`, `main.py`, `company_status_helpers.py`
- **✅ Integration testing:** Added `tests/test_integration_main.py` to catch import/runtime errors in main pipeline
- **✅ Main pipeline verification:** Successfully runs `python main.py msft` without import errors
- **✅ Test fixes:** Resolved pytest collection issues in `test_finnhub.py` by removing `sys.exit(1)` and renaming helper functions
- **✅ Documentation updated:** All documentation reflects new structure and completed modularization
- **✅ All tests passing:** Both unit tests and integration tests pass after reorganization
- **✅ Modularization & refactoring complete:** All refactoring work finished and fully tested
- **🎯 Ready for production:** v3.0.0 is now ready for deployment and user feedback collection

### Key Learnings from v3.0.0 Modularization:
1. **Import path complexity:** Relative imports (`..company.company_profile`) can be tricky when reorganizing modules - use tools to systematically search and fix
2. **Integration testing value:** Simple integration tests that run the main pipeline can catch import errors that unit tests miss
3. **Systematic approach:** Using file search, semantic search, and grep search tools helps identify all import dependencies
4. **Test collection issues:** `sys.exit(1)` in test files can break pytest collection - remove or conditionally use
5. **Incremental verification:** Testing the main pipeline after each batch of import fixes helps isolate issues
6. **Documentation consistency:** Keep documentation updated with completed tasks to track progress accurately

## Version 2.8.2 (June 4, 2025)
- Fixed critical issue with Z-Score report generation that caused duplicate content in reports
- Enhanced DataFrame handling in the reporting pipeline to prevent truthiness ambiguity errors
- Improved context data sanitization before passing to report generation functions
- Better error handling for data type conversions
- Fixed PEP 8 compliance for import statements in reporting module

## Version 2.7.4 (June 3, 2025)
- Major plotting refactor: plotting.py split into helpers and terminal modules
- Full test coverage for plotting_helpers and plotting_terminal
- Improved error handling and modularity in plotting pipeline
- Updated documentation and version numbers for v2.7.4
- No breaking changes; all outputs and APIs remain stable

## Version 2.7.3 (June 3, 2025)
- Codebase cleanup: removed dead code, verified all modules and prompt files are referenced and in use
- Updated documentation and version numbers for v2.7.3

## Version 2.7.1 (June 3, 2025)
- Enhanced executive/officer data injection into LLM qualitative analysis prompts
- Improved company profiles with more comprehensive officer information
- Fixed issue with missing officer data in LLM prompts
- Maintained robust fallback to SEC EDGAR for financials if yfinance fails
- Continued handling of edge cases where only balance sheet data is available from SEC EDGAR
- Error messages for missing or partial financials are propagated to the reporting layer for user clarity

# LEARNINGS.md — Altman Z-Score Analysis (v2.2.2)

## Version 2.2.2 (May 29, 2025)
- All tests pass except for a single fixture warning in test_company_status.py (not release-blocking)
- Script version now included in every report for traceability
- Tested companies documentation and release process are enforced
- Documentation, outputs, and release workflow streamlined and up to date

## Notes
- See README.md for usage and release process
- See PLAN.md and TODO.md for roadmap and actionable tasks

---
All pre-release and tested companies checklist items are now tracked in RELEASE_CHECKLIST.md. See that file for required actions before every release.
---

## Date Formatting in Price Fetching (May 27, 2025)

When working with datetime objects or strings containing time components (e.g., '2025-03-31 00:00:00'), make sure to strip the time portion before passing to APIs or functions expecting 'YYYY-MM-DD' format. We encountered an issue where the `get_quarterly_prices` function in `fetch_prices.py` was receiving dates with time components that caused "unconverted data remains: 00:00:00" errors.

The solution was to modify the function to handle both:
1. String dates with time components (split at space to get just the date part)
2. Datetime objects (format to string without time component)

```python
# Correct way to handle dates with time components
if isinstance(quarter_end, str):
    # Remove any time component if present
    quarter_date = quarter_end.split()[0]
else:
    # For datetime objects, format to string without time component
    quarter_date = pd.to_datetime(quarter_end).strftime('%Y-%m-%d')
```

This approach makes the code more robust when dealing with dates from different sources.

---

## MVP Limitations and Edge Cases (May 2025)

- **Delisted/Nonexistent Tickers:** The pipeline cannot analyze companies that are fully delisted or have no recent filings/market data; it now exits gracefully and saves a user-friendly error report. Some tickers (e.g., RIDE, JHKASD) may have partial or missing data due to delisting, bankruptcy, or symbol changes.
- **No Static Data Fallback:** The pipeline does not use any static or hardcoded financials; if data is missing from APIs, the analysis will not proceed.
- **SIC/Industry Mapping Limitations:** Model selection is based on SIC code and public industry mapping, which may not always reflect true business maturity (e.g., Rivian classified as "mature" due to SIC 3711).
- **Quarterly Data Gaps:** Companies with missing or irregular filings will have gaps in Z-Score trends.
- **International/ADR Support:** The pipeline is designed for US-listed equities; non-US companies may have incomplete data.
- **API/Data Source Reliability:** All results depend on the availability and accuracy of public APIs; outages or changes may affect functionality.

---

## May 2025

- Field names in SEC/XBRL and Yahoo Finance data can vary significantly by company and quarter. Robust mapping and fallback logic are essential.
- Skipping quarters with missing filings early in the pipeline reduces confusion and improves user experience.
- Removing experimental AI features simplified the codebase and improved maintainability.

---

## May 28, 2025: Output Organization and Codebase Cleanup
- All diagnostic and output files are now written directly to per-ticker output folders (output/<TICKER>/).
- All deprecated and backup files were removed from the codebase to avoid confusion.
- The main entry point for the analysis pipeline is now main.py in the project root.
- This improves clarity, reproducibility, and user experience for all future development.

---

## May 29, 2025: LLM Prompt Ingestion and US Ticker Robustness
- Successfully validated that edits to `prompt_fin_analysis.md` are immediately reflected in generated reports for all tested tickers, confirming prompt-driven, user-editable analysis and reporting.
- Ran the full pipeline for a wide range of well-known American companies (MSFT, AAPL, AMZN, TSLA, GOOGL, META, NVDA, SBUX, FDX, DAL) with robust field mapping, fallback logic, and transparent reporting of missing fields. All outputs were generated as expected, with clear warnings for any missing or unmapped data.
- Confirmed that the fallback and partial analysis logic works as intended: the pipeline proceeds with partial Z-Score analysis and flags/reports missing fields in the report, ensuring transparency and reliability.
- The current field mapping, fallback, and reporting logic is robust for US tickers; next focus is on international and bank tickers.

---
