# TODO-Refined

This document consolidates the recommendations from `todo-mvp.md` and `TODO-Codex.md` into a single, prioritized plan. Each action item has been validated against the existing code base and common Python best practices.

## 1. Data Fetching Reliability
- [x] **Retry & Backoff**: Ensure all API calls (Yahoo Finance, SEC) implement retry logic with exponential backoff and capture connection-related exceptions explicitly.  # Implemented in fetchers with retry logic and error handling.
- [ ] **Fallback Sources**: Implement a real SEC EDGAR parser as a fallback when `yfinance` is incomplete. Validate required environment variables (`SEC_EDGAR_USER_AGENT`, `SEC_API_EMAIL`) at startup.
- [x] **Single Price Download**: Fetch the entire date range for price data once and slice locally to minimize network requests.  # Implemented in fetch_prices.py

## 2. Plotting Enhancements
- [x] **Datetime X‑Axis**: Plot Z‑Score and price data using actual dates and enable `ax.xaxis_date()` for proper spacing.  # Implemented in plotting.py
- [x] **Quarter Formatting**: Use `matplotlib.dates.QuarterLocator` and `DateFormatter` to label quarters (e.g. `2024Q1`).  # Implemented in plotting.py
- [x] **Secondary Axis Clarity**: Normalize or scale the price series so it shares the same time axis without distorting the Z‑Score. Clearly label units and legend entries.  # Implemented in plotting.py
- [x] **Pre‑Plot Validation**: Verify that all Z‑Score and price data are present before generating the chart to avoid runtime failures.  # Implemented in plotting.py
- [x] **Improved Price Line**: Enhanced price line visibility with darker color (#444444) and better spacing between data points.  # Implemented in plotting.py
- [x] **I-Shaped Whiskers**: Added I-shaped whiskers with horizontal caps for price range indicators, using thinner lines for better aesthetics.  # Implemented in plotting.py
- [x] **Label Positioning**: Optimized Z-Score and price label positions to prevent overlapping, with Z-Score labels below markers and price labels above.  # Implemented in plotting.py
- [x] **Responsive Y-Axes**: Adjusted y-axis limits and margins to be more responsive to the data range, preventing overlapping between Z-Score and price data.  # Implemented in plotting.py

## 3. Code Structure & Logging
- [x] **Modular Functions**: Refactor large functions (notably `analyze_single_stock_zscore_trend`) into smaller units and remove duplicate logic for model selection.  # Refactored in one_stock_analysis.py
- [x] **Standard Logging**: Replace print statements with the `logging` module and provide a verbose/debug mode for troubleshooting. Log the specific exception types when catching errors.  # logging module used throughout
- [x] **Input Validation**: Validate user inputs and environment variables early in the pipeline to prevent cryptic downstream errors.  # Implemented in CLI and fetchers

## 4. Data Handling Improvements
- [x] **Date Utilities**: Create a shared utility for converting and comparing dates to ensure consistent formats across modules.  # Implemented in utils/time_series.py
- [x] **Type Safety**: Add robust type checking when handling numerical values and dates from external sources.  # Implemented in data_validation.py and fetchers

## 5. Testing & Documentation
- [x] **Unit Tests**: Add tests for the new date utilities and for the date‑alignment logic in the plotting module.  # Implemented in scripts/test_data_validation.py
- [x] **Integration Tests**: Verify the end‑to‑end pipeline including data fetching, caching, and plotting, using mock data where feasible.  # Implemented and run for v1
- [x] **Documentation**: Expand docstrings in critical modules (fetchers and plotting) and document common error scenarios with troubleshooting steps. Include example usage covering typical edge cases.  # Docstrings and usage examples updated

## Priority Actions
1. Implement datetime‑based plotting with proper quarter labels.  # Complete
2. Improve network resilience by adding retries, explicit exception handling, and optional caching for API calls.  # Complete
3. Refactor large functions and unify logging with the `logging` module.  # Complete
4. Validate environment variables and user inputs up front.  # Complete
5. Add pre‑plot validation and unit tests for date alignment.  # Complete
