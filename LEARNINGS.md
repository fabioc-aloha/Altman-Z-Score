# LEARNINGS.md

This file is for documenting key technical and project learnings during the 2025+ refactor of the Altman Z-Score project.

- Capture lessons from new library integrations, API quirks, and data validation challenges.
- Summarize what worked, what didn’t, and why decisions were made.
- Use this as a living document to inform future contributors and avoid repeating past mistakes.
- When fetching market cap or price data for a specific date, always check if the date is a weekend, holiday, or non-trading day. Fallback to the most recent previous trading day and warn the user. This is now implemented in YahooFinanceClient and should be standard for all future data fetchers. Consider using a trading calendar for even more robust handling.

---

## MVP Limitations and Edge Cases (May 2025)

- **Delisted/Nonexistent Tickers:** The pipeline cannot analyze companies that are fully delisted or have no recent filings/market data; it now exits gracefully and saves a user-friendly error report. Some tickers (e.g., RIDE, JHKASD) may have partial or missing data due to delisting, bankruptcy, or symbol changes.
- **No Static Data Fallback:** The pipeline does not use any static or hardcoded financials; if data is missing from APIs, the analysis will not proceed.
- **SIC/Industry Mapping Limitations:** Model selection is based on SIC code and public industry mapping, which may not always reflect true business maturity (e.g., Rivian classified as "mature" due to SIC 3711).
- **Quarterly Data Gaps:** Companies with missing or irregular filings will have gaps in Z-Score trends.
- **International/ADR Support:** The pipeline is designed for US-listed equities; non-US companies may have incomplete data.
- **API/Data Source Reliability:** All results depend on the availability and accuracy of public APIs; outages or changes may affect functionality.

---
