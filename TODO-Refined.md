# TODO-Refined

This document consolidates the recommendations from `todo-mvp.md` and `TODO-Codex.md` into a single, prioritized plan. Each action item has been validated against the existing code base and common Python best practices.

## 1. Data Fetching Reliability
- [ ] **Retry & Backoff**: Ensure all API calls (Yahoo Finance, SEC) implement retry logic with exponential backoff and capture connection-related exceptions explicitly.
- [ ] **Optional Caching**: Add a simple on-disk cache (e.g. `./.cache`) for financial statements and price data to reduce repeated network calls.
- [ ] **Fallback Sources**: Implement a real SEC EDGAR parser as a fallback when `yfinance` is incomplete. Validate required environment variables (`SEC_EDGAR_USER_AGENT`, `SEC_API_EMAIL`) at startup.
- [ ] **Single Price Download**: Fetch the entire date range for price data once and slice locally to minimize network requests.

## 2. Plotting Enhancements
- [ ] **Datetime X‑Axis**: Plot Z‑Score and price data using actual dates and enable `ax.xaxis_date()` for proper spacing.
- [ ] **Quarter Formatting**: Use `matplotlib.dates.QuarterLocator` and `DateFormatter` to label quarters (e.g. `2024Q1`).
- [ ] **Secondary Axis Clarity**: Normalize or scale the price series so it shares the same time axis without distorting the Z‑Score. Clearly label units and legend entries.
- [ ] **Pre‑Plot Validation**: Verify that all Z‑Score and price data are present before generating the chart to avoid runtime failures.

## 3. Code Structure & Logging
- [ ] **Modular Functions**: Refactor large functions (notably `analyze_single_stock_zscore_trend`) into smaller units and remove duplicate logic for model selection.
- [ ] **Standard Logging**: Replace print statements with the `logging` module and provide a verbose/debug mode for troubleshooting. Log the specific exception types when catching errors.
- [ ] **Input Validation**: Validate user inputs and environment variables early in the pipeline to prevent cryptic downstream errors.

## 4. Data Handling Improvements
- [ ] **Date Utilities**: Create a shared utility for converting and comparing dates to ensure consistent formats across modules.
- [ ] **Type Safety**: Add robust type checking when handling numerical values and dates from external sources.

## 5. Testing & Documentation
- [ ] **Unit Tests**: Add tests for the new date utilities and for the date‑alignment logic in the plotting module.
- [ ] **Integration Tests**: Verify the end‑to‑end pipeline including data fetching, caching, and plotting, using mock data where feasible.
- [ ] **Documentation**: Expand docstrings in critical modules (fetchers and plotting) and document common error scenarios with troubleshooting steps. Include example usage covering typical edge cases.

## Priority Actions
1. Implement datetime‑based plotting with proper quarter labels.
2. Improve network resilience by adding retries, explicit exception handling, and optional caching for API calls.
3. Refactor large functions and unify logging with the `logging` module.
4. Validate environment variables and user inputs up front.
5. Add pre‑plot validation and unit tests for date alignment.
