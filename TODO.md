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
- [x] All deprecated files and backups removed from codebase (May 28, 2025)
- [x] All diagnostic and output files are now written directly to per-ticker output folders
- [x] Main entry point is now main.py in the project root; usage is documented

## MVP & v1 Status (as of May 27, 2025)
- [x] MVP: Single-Stock Z-Score Trend Analysis (complete)
- [x] v1: Overlay Stock Price Trend (complete)
- All reporting, charting, and error handling features for the MVP and v1 are implemented and tested.
- Documentation, testing, and incremental rollout policies are strictly followed.

## v2: Enhanced Reporting (Full report file generation)
- [x] Comprehensive, well-formatted report saved as `output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt`
- [x] Includes context, field mapping, Z-Score component table with risk area diagnostics, and all formulas
- [x] Improved field mapping and value formatting

## v2.5: Z-Score Forecasting, Sentiment, and Plotting Enhancements
- [ ] Review and finalize requirements for Z-Score forecasting (define data sources, model, and output format)
- [ ] Research and select APIs for consensus estimates and news/sentiment (e.g., Yahoo Finance, NewsAPI, others)
- [ ] Design forecasting model (lightweight, explainable, and robust)
- [ ] Scaffold new modules for forecasting and sentiment analysis
- [ ] Add/expand tests for new v2.5 features
- [ ] Update documentation (README, PLAN.md, etc.) for v2.5 features and usage
- [ ] Ensure all v1 and v2 features remain stable and well-tested during v2.5 development

## Future Enhancements (beyond v2.5)
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
All deprecated files removed and outputs are now per-ticker as of May 28, 2025.
Use this list for v2 and future progress tracking.
