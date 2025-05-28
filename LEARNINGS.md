# LEARNINGS.md

This file is for documenting key technical and project learnings during the 2025+ refactor of the Altman Z-Score project.

- Capture lessons from new library integrations, API quirks, and data validation challenges.
- Summarize what worked, what didn’t, and why decisions were made.
- Use this as a living document to inform future contributors and avoid repeating past mistakes.
- When fetching market cap or price data for a specific date, always check if the date is a weekend, holiday, or non-trading day. Fallback to the most recent previous trading day and warn the user. This is now implemented in YahooFinanceClient and should be standard for all future data fetchers. Consider using a trading calendar for even more robust handling.

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
