# Altman Z-Score MVP TODO List (2025)

## May 2025 Updates
- [x] Remove srcai/ and ai_bootstrap.py (AI parsing pipeline)
- [x] Expand required_fields mapping for TSLA and AAPL
- [x] Improve logic to skip quarters with missing filings early
- [x] Enhanced reporting: always show industry name (mapped from SIC code) in all reports
- [x] Context section now combines industry and SIC code into a single line
- [x] Z-Score Component Table's Diagnostic column displays the risk area (Safe Zone, Distress Zone, Grey Zone) for each quarter
- [x] All output is clearer, well-formatted, and robust, with improved field mapping and value formatting
- [x] Full analysis report is saved as output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt
- [x] Other key output files: summary, profile, CSV/JSON, and trend chart for each ticker

## MVP & v1 Status (as of May 27, 2025)
- [x] MVP: Single-Stock Z-Score Trend Analysis (complete)
- [x] v1: Overlay Stock Price Trend (complete)
- All reporting, charting, and error handling features for the MVP and v1 are implemented and tested.
- Documentation, testing, and incremental rollout policies are strictly followed.

---
<<<<<<< HEAD
## v2 Roadmap: Z-Score Forecasting & Sentiment Analysis (May 2025)
- [ ] **Requirements Review:** Finalize requirements for Z-Score forecasting (define data sources, model, and output format)
- [ ] **API Research:** Evaluate and select APIs for consensus estimates and news/sentiment (Yahoo Finance, NewsAPI, others)
- [ ] **Design:** Draft a lightweight, explainable, and robust forecasting model. Define clear interfaces for new modules.
- [ ] **Scaffolding:** Scaffold new modules for forecasting and sentiment analysis, following the established modular/testable pattern
- [ ] **Testing:** Add/expand tests for all new v2 features. Ensure v1 features remain stable and well-tested during v2 development
- [ ] **Documentation:** Update README, PLAN.md, and TODO.md for v2 features, usage, and architecture

### v2 Feature Goals
- Z-Score forecasting using consensus estimates and/or time series models
- News and sentiment integration for risk/diagnostic context
- Extensible architecture for future portfolio/multi-ticker analysis
- Maintain and improve reporting, error handling, and documentation standards
=======
## v2 Preparation: Z-Score Forecasting, Sentiment, and Plotting Enhancements
- [ ] **Monthly Stock Price Averages with Whiskers:**
    - [ ] Implement function to aggregate daily prices into monthly averages, min, and max (see fetch_prices.py)
    - [ ] Add overlay of monthly average price points and min/max whiskers to the stock price line in the trend plot (plotting.py)
    - [ ] Add option to enable/disable this overlay in the CLI and plotting function
    - [ ] Unit test aggregation logic and visual test for plot output
    - [ ] Document feature in README and code docstrings
- [ ] Review and finalize requirements for Z-Score forecasting (define data sources, model, and output format)
- [ ] Research and select APIs for consensus estimates and news/sentiment (e.g., Yahoo Finance, NewsAPI, others)
- [ ] Design forecasting model (lightweight, explainable, and robust)
- [ ] Scaffold new modules for forecasting and sentiment analysis
- [ ] Add/expand tests for new v2 features
- [ ] Update documentation (README, PLAN.md, etc.) for v2 features and usage
- [ ] Ensure all v1 features remain stable and well-tested during v2 development
>>>>>>> 671cc1f (Refactor: remove deprecated files, clean up diagnostics output, and clarify main entry point. All outputs now organized per ticker. Deprecated modules removed.)

---
## Future Enhancements (beyond v2)
- [ ] Portfolio/multi-ticker analysis
- [ ] Advanced correlation and insights
- [ ] Community contributions and plugin support

---
## 5. Testing & Documentation
- [x] **Unit Tests**: Add tests for the new date utilities and for the date‑alignment logic in the plotting module.  # Implemented in scripts/test_data_validation.py
- [x] **Integration Tests**: Verify the end‑to‑end pipeline including data fetching, caching, and plotting, using mock data where feasible.  # Implemented and run for v1
- [x] **Documentation**: Expand docstrings in critical modules (fetchers, plotting, analysis, z-score computation) and document common error scenarios with troubleshooting steps. All core docstrings and comments have been reviewed and updated for clarity, accuracy, and maintainability.  # Complete as of May 2025

MVP is complete as of May 24, 2025.
v1 Stock Price Overlay feature completed on May 27, 2025.
Use this list for v2 and future progress tracking.
