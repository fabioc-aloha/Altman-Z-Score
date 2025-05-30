# Vision: Exceeding the Competition

Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

> See [vision.md](./vision.md) for the full vision statement. Do not include the vision in other documentation.

# PLAN.md — Altman Z-Score Analysis (v2.4)

## Short-Term Action Items (for TODO.md)
- Add warnings for size/leverage outliers in the report
- Expand unit/integration tests for new model selection and reporting logic
- Integrate additional industry benchmark data (WRDS/Compustat or open data) into constants.py as available
- Document and automate calibration update process in altmans.md
- Schedule periodic calibration updates and document the process
- Continue to refine transparency and reporting for edge cases
- Expand FIELD_SYNONYMS and mapping logic for international/bank tickers (add multi-language, sector-aware mapping, and user overrides)
- Add/expand tests for prompt ingestion, mapping, and reporting
- Improve documentation for mapping, prompt usage, and internationalization
- Modularize data connectors and enhance CLI for batch/portfolio analysis
- Prepare for web dashboard, REST API, and Excel Add-In (see competition roadmap.md)
- Begin v2.5: Z-Score forecasting, sentiment/news analysis, and multi-ticker/portfolio support

## Current Version: v2.4 (May 30, 2025)
- Weekly-only simplification, CLI/pipeline/docs/tests updated, dispatcher/model logic improved
- All plotting and reporting logic updated for weekly-only data
- All documentation and tests updated for weekly-only support

## v2.5 Roadmap: Forecasting, Sentiment, and Portfolio Analysis
- Forecasting: Add ability to forecast next quarter's Z-Score using consensus estimates and/or time series models
- Sentiment & News Analysis: Integrate news and sentiment APIs, correlate with Z-Score and price trends
- Portfolio/Multi-Ticker Analysis: Generalize pipeline for multiple tickers, output per-ticker and aggregate summaries
- Testing & Documentation: Add/expand tests for new v2.5 features, update documentation for v2.5 features and usage

## Implementation Principles
- Simplicity: Start with a single-stock analysis pipeline, then generalize to portfolios
- Modularity: Clean separation of data fetching, validation, computation, and reporting
- Testability: Each module is independently testable with clear interfaces
- Robustness: Strong error handling, logging, and data validation at every step
- Extensibility: Easy to add new data sources, models, or output formats

## Architecture Overview
1. Input Layer: Accepts ticker(s) and analysis date; validates input
2. Data Fetching Layer: Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance)
3. Validation Layer: Validates raw data using Pydantic schemas; reports missing/invalid fields
4. Computation Layer: Computes Altman Z-Score using validated data; returns result object
5. Reporting Layer: Outputs results to CSV, JSON, or stdout; logs all steps and errors

## Conservative, Incremental Rollout Policy
- Build a minimal, robust MVP first (single-stock Z-Score trend analysis)
- Test thoroughly at each step before enabling new features
- Only enable new features after the MVP is stable and well-tested
- Light up features one at a time, with tests and documentation, to avoid regressions
- Avoid over-ambitious changes; prioritize reliability and maintainability

# ---
# All pre-release and tested companies checklist items are now tracked in RELEASE_CHECKLIST.md. See that file for required actions before every release.
