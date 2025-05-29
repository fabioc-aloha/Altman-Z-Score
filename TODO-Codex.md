# TODO-Codex

This document captures a quick review of the current codebase for the Altman Z-Score project. The goal is to highlight areas that affect MVP stability and data reliability when fetching from external APIs, and to outline recommendations for improving the upcoming stock price overlay plotting.

## 1. Review of Data Fetching Logic

### Financial Statements (`src/altman_zscore/fetch_financials.py`)
* Primary source is `yfinance`. The module logs available columns and attempts a limited SEC EDGAR fallback when yfinance data is missing. However full SEC XBRL parsing is not implemented yet and the fallback raises an error.
* There is basic logging and a warning when partial data is returned. Errors generally result in `None` so the calling code can exit gracefully.
* Considerations for stability:
  - Implement retries and explicit handling for transient network failures.
  - Integrate a lightweight caching layer so repeated runs do not hammer the APIs.
  - Provide a real SEC EDGAR parser to improve reliability for delisted or thinly traded tickers.
  - Validate environment variables for user agent and request rate so API calls comply with SEC rules.

### Market Prices (`src/altman_zscore/fetch_prices.py`)
* Uses yfinance with retry logic around `yf.download`. It increases the date buffer and sleeps with exponential backoff.
* `get_quarterly_prices` downloads data for every quarter individually. This can cause many network calls and slow execution.
* Improvements:
  - Fetch the full date range in one call and slice locally to reduce network requests.
  - Explicitly catch HTTP and connection errors, returning informative messages.
  - Allow optional caching of downloaded price data (e.g., in `./.cache`).

### SEC API Client (`src/altman_zscore/api/sec_client.py`)
* Implements rate limiting via a token bucket and enforces the SEC 10‑requests/sec policy.
* Looks up CIKs and company facts with clear error handling. User agent string is required via environment variables.
* Recommendation: add unit tests for rate limit handling and provide better recovery on 429/503 responses.

### Yahoo Client (`src/altman_zscore/api/yahoo_client.py`)
* Fetches market cap around a given date using a moving window. Falls back to `info["marketCap"]` when historical data is absent.
* Suggest adding retries with backoff and logging when a fallback is used so the final result is auditable.

Overall the MVP pipeline is functional but can benefit from unified retry logic, caching, and more robust fallbacks to guarantee consistent data retrieval.

## 2. Plotting Improvements for Stock Price Overlay

The function `plot_zscore_trend` in `src/altman_zscore/plotting.py` has been enhanced with the following improvements:

✓ **Use datetime-based x‑axis** – Plot both Z‑Score and stock price series with `quarter_end` converted to real dates.
✓ **Quarter formatting** – Format tick labels to show proper dates.
✓ **Single download for price data** – Fetch all price data for the full analysis period in one request.
✓ **Consistent scaling** – When plotting prices, normalize and scale the values with appropriate margins to prevent overlapping.
✓ **Legend clarity** – Added units to the price axis label and clear legend distinction between Z‑Score line and stock price.
✓ **Enhanced visuals** – Implemented I-shaped whiskers, optimized label positions, and improved color scheme for better readability.

Additional improvements that could be considered:
- Add option to show moving averages for both Z-Score and price trends
- Enable interactive tooltips when viewing in notebooks
- Add ability to highlight specific events or periods
- Support for comparing multiple stocks' Z-Scores in a single plot

