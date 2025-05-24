# Altman Z-Score MVP TODO List (2025)

## Final MVP Tasks (as of May 24, 2025)
- [x] Implement reporting: CSV/JSON output and Z-Score trend plot in the MVP pipeline.
- [x] Validate pipeline output for Sonos and other real-world tickers.  # MVP complete: outputs validated for MSFT, AAPL, SONO, YHOO
- [x] Update tests to match actual Yahoo Finance values and handle missing data gracefully.  # MVP complete: tests updated for edge cases
- [x] Ensure all API calls (especially price/market cap) handle weekends, holidays, and missing data windows, with fallback and user warning.
- [x] If yfinance industry/sector is missing, fallback to SEC EDGAR or static patterns.
- [x] Update PLAN.md and TODO.md as you complete each step.

## Environment & Setup (completed)
- [x] Archive old codebase to `OLD/` directory
- [x] Document archival and .env usage in README.md
- [x] Create and document `.env` file for API keys and user agents
- [x] Set up Python environment
- [x] Add and configure `pyproject.toml` for dependencies
- [x] Add initial dependencies:
  - pandas
  - pydantic
  - requests
  - yfinance
  - sec-edgar-downloader
  - arelle or xbrlparse
  - matplotlib or plotly
  - python-dotenv
- [x] Project now uses a local `.venv` for all development and testing (see `docs/venv_setup.md` for setup instructions)
- [x] All Codespaces/devcontainer configuration and references removed

## MVP Pipeline Scaffold
- [x] Scaffold `src/altman_zscore/one_stock_analysis.py` with pipeline structure
- [x] Scaffold `src/altman_zscore/schemas/validation.py` with Pydantic models
- [x] Implement CLI or function input handling (ticker, date, etc.)
- [x] Implement SEC financials fetcher (using sec-edgar-downloader)
- [x] Implement XBRL parser (arelle/xbrlparse)
- [x] Implement Yahoo Finance price fetcher (yfinance)
- [x] Implement data validation (Pydantic)
- [x] Implement Z-Score computation (with industry/maturity calibration, validated against Sonos case)
- [x] Implement reporting (CSV/JSON output, Z-Score trend plot)

## Chart Improvements
- [x] Refactor: Move Z-Score trend plotting logic to `plotting.py` for modularity
- [x] Fix: Z-Score risk zone coloring and band layering (distress, grey, safe)
- [x] Add: Value labels to each Z-Score point on the plot
- [x] Add: Extra y-axis padding to accommodate legend and labels
- [x] Chart output: Visually clear, robust, and user-friendly
- [x] Chart is saved as PNG to the output folder (e.g., output/zscore_<TICKER>_<DATE>_trend.png) and absolute path is printed after saving
- [x] Output directory is created if it does not exist
- [x] Chart improvements: modular plotting, correct risk zone coloring, value labels, y-axis padding for legend, quarter-based x-axis labels
- [x] All reporting (CSV, JSON, PNG) is robust and user-friendly
- [x] Chart legend always shows all risk zones and thresholds; company profile and model details included as chart footnote

---
## Next Steps: v1 Overlay Stock Price Trend
- [ ] Design and implement overlay of stock price trend on Z-Score chart
- [ ] Fetch historical price data for the same period as Z-Score analysis
- [ ] Update plotting logic to combine Z-Score and price trend (dual y-axis or overlay)
- [ ] Update tests and documentation for v1 features

---
MVP is complete as of May 24, 2025. Use this list for v1 and future progress tracking.
