# Altman Z-Score MVP TODO List (2025)

## Final MVP Tasks (as of May 23, 2025)
- [x] Implement reporting: CSV/JSON output and Z-Score trend plot in the MVP pipeline.
- [ ] Validate pipeline output for Sonos and other real-world tickers.
- [ ] Update tests to match actual Yahoo Finance values and handle missing data gracefully.
- [x] Ensure all API calls (especially price/market cap) handle weekends, holidays, and missing data windows, with fallback and user warning.
- [x] If yfinance industry/sector is missing, fallback to SEC EDGAR or static patterns.
- [x] Update PLAN.md and TODO.md as you complete each step.

## Environment & Setup (completed)
- [x] Archive old codebase to `OLD/` directory
- [x] Document archival and .env usage in README.md
- [x] Create and document `.env` file for API keys and user agents
- [x] Set up Codespaces-compatible Python environment
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

## MVP Pipeline Scaffold
- [x] Scaffold `src/altman_zscore/one_stock_analysis.py` with pipeline structure
- [x] Scaffold `src/altman_zscore/schemas/validation.py` with Pydantic models
- [x] Implement CLI or function input handling (ticker, date, etc.)
- [x] Implement SEC financials fetcher (using sec-edgar-downloader)
- [x] Implement XBRL parser (arelle/xbrlparse)
- [x] Implement Yahoo Finance price fetcher (yfinance)
- [x] Implement data validation (Pydantic)
- [x] Implement Z-Score computation (with industry/maturity calibration, validated against Sonos case)
- [ ] Implement reporting (CSV/JSON output, Z-Score trend plot)

## Model Selection & Calibration
- [x] Implement model selection logic based on company industry, maturity, and public/private status
- [x] Expand company profile/classifier to set industry, is_public, is_emerging_market for real tickers (static mapping + yfinance fallback)
- [x] Implement additional Z-Score models (private, public, service, EM) and calibrations
- [x] Add unit tests for private and public models (Sonos test complete for 'original')

## Testing & Quality
- [x] Add unit test for Sonos Q1 FY2025 (matches literature)
- [x] Add unit tests for other models and edge cases (private, public)
- [x] Add integration test for full pipeline
- [ ] Validate with real-world tickers and edge cases (real data)
- [ ] Validate pipeline output for Sonos against paper/literature values

## New/Outstanding Tasks (enhancements & future improvements)
- [ ] Add real Sonos Q1 FY2025 financials to fetcher for validation
- [ ] Compare pipeline Z-Score output for SONO to paper/literature and document any discrepancies
- [ ] Update tests to match actual Yahoo Finance values (e.g., "Consumer Electronics" for Apple) and handle missing data gracefully.
- [ ] Add SEC EDGAR lookup as a fallback for US tickers if yfinance industry/sector is missing.
- [ ] Use static patterns for known tickers if both yfinance and SEC fail (robust fallback).
- [ ] Reintroduce enums for industry group and market category for consistency and testability.
- [ ] Optionally, add company maturity classification using revenue growth/market cap if available.

## Next Steps (future/optional)
- [ ] Implement real company classification (industry, public/private, emerging market) for all supported tickers
- [ ] Implement real data fetching (SEC, Yahoo) for all supported tickers
- [ ] Implement robust reporting and output formats (CSV/JSON, trend plot)
- [ ] Document calibration sources and assumptions
- [ ] For all future API calls (especially price/market cap fetches), always account for weekends, holidays, and missing data windows. Use a fallback to the most recent previous trading day, and warn the user if fallback is used. Consider using a trading calendar for even more robust handling.

---
Check off each item as you complete it. Use this list for MVP progress tracking and environment setup.
