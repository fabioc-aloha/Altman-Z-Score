# Altman Z-Score MVP TODO List (2025)

## May 29, 2025 Updates
- [x] Enhanced visualization with improved Z-Score and price plotting
- [x] Moved Z-Score labels above markers for better readability
- [x] Implemented I-shaped whiskers for price range indicators
- [x] Made whiskers thinner (1px) with horizontal caps for better aesthetics
- [x] Adjusted color scheme with darker gray (#444444) for price data
- [x] Fixed indentation issues with consistent 4-space indentation
- [x] Added responsive y-axis scaling to prevent overlapping
- [x] Fixed annotate function parameter names (text vs label)
- [x] Included output/ directory in git repository with example reports
- [x] Added "Output Examples" section to README.md

## May 29, 2025: DOCX/Word Export Removal
- [x] DOCX/Word export feature removed from the codebase due to persistent formatting and chart embedding issues.
- [x] All documentation and code references to DOCX/Word export have been removed.
- [x] Reports are now generated in Markdown format only.

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

## V2.1 Status (Current)
- [x] MVP: Single-Stock Z-Score Trend Analysis (complete)
- [x] v1: Overlay Stock Price Trend (complete)
- All reporting, charting, and error handling features for the MVP and v1 are implemented and tested.
- Documentation, testing, and incremental rollout policies are strictly followed.

## V2.2: Model Selection & Calibration Overhaul (2025-05-29)
- [x] Centralized all model coefficients, thresholds, and metadata in `src/altman_zscore/computation/constants.py`.
- [x] Integrated company maturity (early-stage, growth, mature) into model selection logic.
- [x] Model selection now uses industry, SIC, public/private status, region, and maturity.
- [x] Dispatcher in `compute.py` dynamically handles any model key present in `MODEL_COEFFICIENTS`, including new/custom and SIC-specific keys, using the original formula and logging the override.
- [x] NotImplementedError is only raised for truly unknown model keys.
- [x] Reporting and override context are fully logged for transparency.
- [x] All main model constants and thresholds match Altman literature and best practices.
- [x] Structure supports easy addition of new models, coefficients, and thresholds.
- [x] DECISIONS.md is deprecated; all major decisions are now tracked in PLAN.md and TODO.md.
- [ ] Add warnings for size/leverage outliers in the report.
- [ ] Expand unit/integration tests for new model selection and reporting logic.
- [ ] Integrate additional industry benchmark data (WRDS/Compustat or open data) into `constants.py` as available.
- [ ] Document and automate calibration update process in `altmans.md`.
- [ ] Schedule periodic calibration updates and document the process.
- [ ] Continue to refine transparency and reporting for edge cases.

## V2.5: Z-Score Forecasting, Sentiment, and Plotting Enhancements
- [ ] Review and finalize requirements for Z-Score forecasting (define data sources, model, and output format)
- [ ] Research and select APIs for consensus estimates and news/sentiment (e.g., Yahoo Finance, NewsAPI, others)
- [ ] Design forecasting model (lightweight, explainable, and robust)
- [ ] Scaffold new modules for forecasting and sentiment analysis
- [ ] Add/expand tests for new v2.5 features
- [ ] Update documentation (README, PLAN.md, etc.) for v2.5 features and usage
- [ ] Ensure all v2.1 and v2.2 features remain stable and well-tested during v2.5 development
- [ ] Add option to show moving averages for both Z-Score and price trends
- [ ] Enable interactive tooltips when viewing plots in notebooks
- [ ] Add ability to highlight specific events or periods (e.g., earnings releases, management changes)
- [ ] Support for comparing multiple stocks' Z-Scores in a single plot
- [ ] Add data table export option for all chart data
- [ ] Implement dark mode for plots with appropriate color schemes

## V2.6: Portfolio/multi-ticker analysis
- [ ] Generalize pipeline for batch/portfolio analysis

## V2.7: Advanced correlation and insights
- [ ] Correlate Z-Score, price, and operational health metrics

## V2.8: Community contributions and plugin support
- [ ] Enable plugin architecture and community-driven features

## Future Enhancements (beyond v2.8)
- [ ] Portfolio/multi-ticker analysis
- [ ] Advanced correlation and insights
- [ ] Community contributions and plugin support

## 5. Testing & Documentation
- [x] **Unit Tests**: Add tests for the new date utilities and for the date‑alignment logic in the plotting module.  # Implemented in scripts/test_data_validation.py
- [x] **Integration Tests**: Verify the end‑to‑end pipeline including data fetching, caching, and plotting, using mock data where feasible.  # Implemented and run for v1
- [x] **Documentation**: Expand docstrings in critical modules (fetchers, plotting, analysis, z-score computation) and document common error scenarios with troubleshooting steps. All core docstrings and comments have been reviewed and updated for clarity, accuracy, and maintainability.  # Complete as of May 2025

MVP is complete as of May 24, 2025.
v1 Stock Price Overlay feature completed on May 27, 2025.
All deprecated files removed and outputs are now per-ticker as of May 28, 2025.
Use this list for v2 and future progress tracking.

# Prompt Ingestion for LLM Analysis: Test Checklist

## Goal
Ensure that edits to `prompt_fin_analysis.md` are reflected in the generated financial analysis and recommendations section of the report.

## Test Steps
1. **Edit the Prompt**
    - Open `prompt_fin_analysis.md` and add a unique phrase (e.g., "TEST-PROMPT-INGESTION-123").
2. **Run the Analysis Pipeline**
    - Execute the pipeline for any ticker (e.g., `python main.py MSFT`).
3. **Check the Output Report**
    - Open the generated report in `output/<TICKER>/zscore_<TICKER>_zscore_full_report.md` (or `.txt`).
    - Confirm that the LLM-generated financial analysis section contains the unique phrase you added.
4. **Revert the Prompt**
    - Remove the test phrase from `prompt_fin_analysis.md` to restore the canonical prompt.

## Expected Result
- The LLM analysis section in the report should reflect any changes made to `prompt_fin_analysis.md` without requiring a code change or restart.

## Notes
- If the phrase does not appear, check for errors in the pipeline or LLM call.
- This test ensures full transparency and user control over the LLM's analysis instructions and references.

---

