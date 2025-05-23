# yfinance API: Industry and Sector Field Documentation

## Source
- [yfinance GitHub](https://github.com/ranaroussi/yfinance)
- [yfinance Documentation](https://ranaroussi.github.io/yfinance/)

## Key Points
- `yfinance.Ticker.info` returns a dictionary with many fields, including `industry`, `sector`, and `country`.
- The values for `industry` and `sector` are not standardized and are populated directly from Yahoo Finance's backend.
- Either or both fields may be missing (i.e., not present or set to `None`).
- There is no fallback value like `"Unknown"`—if missing, the field is simply absent or `None`.
- The possible values for `industry` and `sector` are not documented and may change over time. Examples include:
  - Industry: "Consumer Electronics", "Technology", "Banks—Diversified", etc.
  - Sector: "Technology", "Financial Services", etc.
- For some tickers (especially non-US or less popular stocks), both fields may be missing.
- If both are missing, the code should handle this gracefully (e.g., raise a clear error, log, or skip).
- When writing tests, match the actual Yahoo Finance value (e.g., "Consumer Electronics" for Apple) rather than a hardcoded expectation.

## Example Usage
```python
import yfinance as yf
yf_ticker = yf.Ticker('AAPL')
yf_info = yf_ticker.info
industry = yf_info.get('industry')  # e.g., 'Consumer Electronics'
sector = yf_info.get('sector')      # e.g., 'Technology'
country = yf_info.get('country')    # e.g., 'United States'
```

## Recommendations
- Do not assume a fixed set of values for `industry` or `sector`.
- Always log or inspect the actual values returned for transparency and debugging.
- Update tests to reflect the real values from Yahoo Finance.
- If both fields are missing, raise a clear error and include the full `yf_info` in the message for diagnostics.

---
_Last updated: 2025-05-23_
