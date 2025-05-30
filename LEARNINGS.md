# LEARNINGS.md — Altman Z-Score Analysis (v2.2.2)

## Version 2.2.2 (May 29, 2025)
- All tests pass except for a single fixture warning in test_company_status.py (not release-blocking)
- Script version now included in every report for traceability
- Tested companies documentation and release process are enforced
- Documentation, outputs, and release workflow streamlined and up to date

## Notes
- See README.md for usage and release process
- See PLAN.md and TODO.md for roadmap and actionable tasks
- See output/TESTED_COMPANIES.md for tested companies and outcomes

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
