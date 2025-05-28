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
## v2 Preparation: Z-Score Forecasting & Sentiment Analysis
- [ ] Review and finalize requirements for Z-Score forecasting (define data sources, model, and output format)
- [ ] Research and select APIs for consensus estimates and news/sentiment (e.g., Yahoo Finance, NewsAPI, others)
- [ ] Design forecasting model (lightweight, explainable, and robust)
- [ ] Scaffold new modules for forecasting and sentiment analysis
- [ ] Add/expand tests for new v2 features
- [ ] Update documentation (README, PLAN.md, etc.) for v2 features and usage
- [ ] Ensure all v1 features remain stable and well-tested during v2 development

---
## Future Enhancements (beyond v2)
- [ ] Portfolio/multi-ticker analysis
- [ ] Advanced correlation and insights
- [ ] Community contributions and plugin support

---
MVP is complete as of May 24, 2025.
v1 Stock Price Overlay feature completed on May 27, 2025.
Use this list for v2 and future progress tracking.
