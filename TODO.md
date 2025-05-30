# Vision Alignment

All tasks and phases in this TODO are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

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

## V2.3: Weekly Price Data Integration (2025-05-30) ✅ COMPLETED
- [x] **Weekly Price Data Functionality**: Implemented `get_weekly_price_stats()` function with Monday-start week grouping
- [x] **Enhanced Plotting**: Updated `plot_zscore_trend()` to support weekly price overlays with automatic data selection
- [x] **Pipeline Integration**: Added weekly data fetching and saving to main analysis pipeline
- [x] **Comprehensive Testing**: Created `weekly_demo.py` for full integration demonstration
- [x] **Data Persistence**: Weekly data saved as CSV/JSON alongside monthly/quarterly data
- [x] **Backward Compatibility**: All existing functionality preserved, weekly features are additive
- [x] **Documentation**: Created `WEEKLY_INTEGRATION_SUMMARY.md` with complete implementation details
- [x] **Main Pipeline Testing**: Verified end-to-end functionality with `python main.py MSFT` and `python main.py TSLA`
- [x] **Import Resolution**: Resolved all module import issues for seamless integration

**V2.3 Status**: All weekly price data features are now fully integrated and operational in the main pipeline. Weekly data provides up to 58 weeks of recent price history (vs 14 months for monthly data), offering higher granularity for trend analysis.

## V2.4: Weekly-Only Simplification (2025-05-30) ✅ COMPLETED
- [x] **Codebase Simplification**: Removed monthly price functionality to simplify codebase and focus on weekly data
- [x] **Function Signature Updates**: Removed `monthly_stats` parameter from `plot_zscore_trend()` and `plot_zscore_trend_pipeline()`
- [x] **Monthly Function Removal**: Deleted `get_monthly_price_stats()` functions from both `data_fetching/prices.py` and `fetch_prices.py`
- [x] **Import Cleanup**: Removed all monthly function imports throughout the codebase
- [x] **Test Updates**: Updated `test_plot_visualizations.py` to use weekly data instead of monthly
- [x] **Pipeline Simplification**: Modified `one_stock_analysis.py` to only fetch and use weekly price data
- [x] **Main Script Updates**: Fixed syntax errors and removed `--monthly` argument parsing from `main.py`
- [x] **File Cleanup**: Removed obsolete `scripts/test_monthly_prices.py` file
- [x] **Plotting Logic**: Simplified price overlay logic to always use weekly approach with consistent labeling
- [x] **Documentation**: Updated function docstrings to reflect weekly-only support
- [x] **Parameter Cleanup**: Removed `weekly_stats` parameter from plotting functions, simplified to use only `stock_prices` parameter
- [x] **CLI Simplification**: Removed `--weekly` parameter from main.py CLI since weekly functionality is always enabled
- [x] **Quarterly Prices Removal**: Removed unused `get_quarterly_prices()` function and all quarterly price file generation (Option 2)
  - [x] Removed `get_quarterly_prices` import from `one_stock_analysis.py`
  - [x] Removed quarterly price function calls and file saving logic from main analysis pipeline  
  - [x] Deleted `get_quarterly_prices()` function definitions from both `data_fetching/prices.py` and legacy `fetch_prices.py`
  - [x] Updated test files to check for weekly prices instead of quarterly prices
  - [x] Cleaned up all existing `quarterly_prices.csv` and `quarterly_prices.json` files from output directories
  - [x] Verified main analysis functionality works correctly without quarterly prices

**V2.4 Status**: Codebase successfully simplified to support only weekly price overlays. This reduces complexity while maintaining the higher granularity benefits of weekly data. Monthly functionality has been completely removed, making the codebase more maintainable and focused. The `weekly_stats` parameter has been removed from plotting functions and the `--weekly` CLI parameter has been removed to further simplify the API.
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

# TODO.md — Altman Z-Score Analysis (v2.2.2)

## Version 2.2.2 (May 29, 2025)
- Script version now included in every report for traceability
- Tested companies documentation and release process are enforced
- Documentation, outputs, and release workflow streamlined and up to date
- All changes are fully tracked and versioned in outputs and documentation

## Next Steps
- See PLAN.md for roadmap and high-level features
- See output/TESTED_COMPANIES.md for tested companies and outcomes
- All pre-release and tested companies checklist items are now tracked in RELEASE_CHECKLIST.md. See that file for required actions before every release.

---

## Completed (v2.2.1)
- Centralized all LLM prompt files in `src/prompts/` and made them user-editable; updated code to ingest prompts from there.
- Refactored prompt ingestion logic for robust path handling and runtime updates.
- Updated documentation (`README.md`, `PLAN.md`, `TODO.md`) to describe the new prompt workflow and folder structure.
- Added a test checklist for prompt ingestion.
- Fixed a bug with prompt path logic for financial analysis.
- Moved chart image/caption before the LLM analysis in the report and into its own section.
- Made the LLM generate all section names, including references and disclaimers, per prompt instructions.
- Removed all hardcoded references, disclaimers, and section headings from the code.
- Improved terminal output to only show save status, not report content.
- Fixed yfinance/pandas warnings in `prices.py`.
- Updated the financial analysis prompt to require a disclaimer, references, and context-aware stakeholder tables, and to include source attribution and author.
- Updated the field mapping prompt to instruct the LLM to use semantic similarity/context, not just string matching.
- Removed the DOCX/Word export feature and all related code/docs.
- Added a hardcoded introduction and source attribution (with author) to the top of the report in `reporting.py`.
- Made the source attribution and project/author reference consistent in both the prompt and the report.
- Removed the "Missing" column from the Raw Data Field Mapping Table in the report generator.
- Ensured the introduction and attribution are always at the very top of the generated report file and included in the LLM context.
- Added a developer disclaimer to the introduction.
- Updated the LICENSE to a custom "Attribution Non-Commercial License (MIT-based)" and referenced it in the report introduction.
- Moved the report title to the very top of the report, before the introduction, with correct line spacing.
- Fixed the report generator to ensure only one introduction section appears, immediately after the title, and not duplicated.
- Renamed the section "Analysis Context and Decisions" to "Analysis Context and Z-Score Model Selection Criteria".
- Staged, committed, and pushed changes to the main branch, including updated reports and documentation.
- Updated the version to 2.2.1 in all documentation and changelogs.
- **Successfully ran the pipeline and generated full reports for a wide range of well-known American companies (MSFT, AAPL, AMZN, TSLA, GOOGL, META, NVDA, SBUX, FDX, DAL), confirming robust field mapping, fallback, and reporting logic for these cases.**

## Version 2.2.1 (May 29, 2025)
- [x] Centralize all LLM prompt files in `src/prompts/` and make them user-editable
- [x] Refactor prompt ingestion logic for robust path handling and runtime updates
- [x] Update documentation (`README.md`, `PLAN.md`, `TODO.md`) to describe the new prompt workflow, folder structure, and version 2.2.1
- [x] Add a test checklist for prompt ingestion
- [x] Fix bugs with prompt path logic and yfinance/pandas warnings
- [x] Move chart image/caption before the LLM analysis in the report and into its own section
- [x] Make the LLM generate all section names, including references and disclaimers, per prompt instructions
- [x] Remove all hardcoded references, disclaimers, and section headings from the code
- [x] Improve terminal output to only show save status, not report content
- [x] Update the financial analysis prompt to require a disclaimer, references, context-aware stakeholder tables, and to include source attribution and author
- [x] Update the field mapping prompt to instruct the LLM to use semantic similarity/context, not just string matching
- [x] Remove the DOCX/Word export feature and all related code/docs
- [x] Add a hardcoded introduction, source attribution, author, and license to the top of the report in `reporting.py`
- [x] Make the source attribution and project/author reference consistent in both the prompt and the report
- [x] Remove the "Missing" column from the Raw Data Field Mapping Table in the report generator
- [x] Ensure the introduction and attribution are always at the very top of the generated report file and included in the LLM context
- [x] Add a developer disclaimer to the introduction
- [x] Update the LICENSE to a custom "Attribution Non-Commercial License (MIT-based)" and reference it in the report introduction
- [x] Move the report title to the very top of the report, before the introduction, with correct line spacing
- [x] Fix the report generator to ensure only one introduction section appears, immediately after the title, and not duplicated
- [x] Rename the section "Analysis Context and Decisions" to "Analysis Context and Z-Score Model Selection Criteria"
- [x] Stage, commit, and push changes to the main branch, including updated reports and documentation
- [x] Update the version to 2.2.1 in all documentation and changelogs

### Prompt Folder Usage
- All LLM prompt files are now in `src/prompts/`.
- Edit these files to change LLM instructions, references, or output style—changes are reflected immediately in new reports.
- Add new prompt files in `src/prompts/` for new LLM-driven features and reference them in code.

## In Progress / Next
- [ ] Expand test coverage for prompt ingestion and runtime updates
- [ ] Add more prompt-driven features (e.g., qualitative commentary, advanced diagnostics)
- [ ] Continue improving Codespaces compatibility and documentation
- [ ] Prepare for v2.2.x: outlier warnings, expanded tests, and further reporting improvements
- [ ] **Next: Focus on international and bank tickers, as US tickers are now well covered and tested.**

## Prompt Folder Usage
- All LLM prompt files are in `src/prompts/`.
- To customize LLM behavior, edit the relevant prompt file. Changes are reflected immediately in all outputs.
- For new LLM-driven features, add a new prompt file in `src/prompts/` and reference it in your code.

## May 29, 2025: Field Mapping & Internationalization Next Steps
- [ ] Expand FIELD_SYNONYMS in openai_client.py for all canonical fields, especially for banks and international companies (add Portuguese, Spanish, French, etc.; e.g., "Receita de Juros", "Lucro Líquido").
- [ ] Implement bank/financial institution awareness: detect banks from sector/industry/ticker and adjust mapping priorities (e.g., map 'sales' to 'Interest Income' if no revenue field is present).
- [ ] Add partial/fallback mapping reporting: when a field cannot be mapped, include a 'Reason' in the returned mapping and surface this in the report.
- [ ] Use sample_values (if provided) to improve mapping confidence (e.g., match by value type/range).
- [ ] Normalize field names for case-insensitive and accent-insensitive matching before mapping.
- [ ] Add granular logging for mapping decisions, especially for fallbacks and unmapped fields.
- [ ] Allow user to provide a mapping override file (e.g., mapping_overrides.json) for persistent issues.
- [ ] Add/expand unit tests for mapping logic, especially for international tickers and banks.
- [ ] If LLM response is malformed/missing, fall back to code-level synonym matching and log a warning.
- [ ] Document mapping logic, fallback rules, and internationalization in README or a dedicated doc.

# Competitive Roadmap Tasks (Source: competition roadmap.md)

## Phase 1: Foundation
- [ ] Implement modular data connectors for Alpha Vantage, IEX Cloud, CSV, SQL, REST
- [ ] Build and document Public REST API v1 for Z-Score calculations
- [ ] Enhance CLI for batch processing, per-ticker outputs, and summary reports
- [ ] Expand documentation with quickstarts, in-tool help, and guided tutorials

## Phase 2: Interactivity
- [ ] Develop web dashboard with interactive charts and peer comparisons
- [ ] Create Excel Add-In for one-click report generation
- [ ] Implement alerting system (email/Slack notifications)

## Phase 3: Intelligence
- [ ] Integrate LLM-powered AI narrative generation for Z-Score summaries
- [ ] Prepare SaaS tier with hosted deployment, SLAs, and RBAC

## Phase 4: Enterprise & Extensibility
- [ ] Develop pro plugins for advanced stress-testing and scenario analysis
- [ ] Enable audit-ready exports with versioning, change logs, and metadata
- [ ] Integrate with BI platforms (Power BI, Tableau)
- [ ] Prepare for marketplace deployment (Azure Marketplace, automated scripts)

## Phase 5: Scale & Partnerships
- [ ] Add real-time data feed support (WebSocket, premium feeds)
- [ ] Upgrade API to v2 (bulk endpoints, streaming, improved handling)
- [ ] Make dashboard mobile-responsive

## Competitive Differentiators (Implementation)
- [ ] Ensure zero licensing cost for open-source core and open-core add-ons
- [ ] Maintain modular data flexibility (plug-and-play connectors)
- [ ] Deliver AI-driven insights (automated summaries, alerting)
- [ ] Foster community-driven roadmap (public roadmap, sprints, early access)
- [ ] Package enterprise features (SaaS, SLAs, RBAC, audit-ready, BI integration)

## Non-Functional Requirements
- [ ] Optimize for efficient batch processing (100+ tickers)
- [ ] Enforce OAuth2 and TLS for SaaS/API
- [ ] Architect for horizontal scaling (API/UI)
- [ ] Target System Usability Scale (SUS) score ≥ 80
- [ ] Document and monitor SaaS uptime commitment

> For full details, see `competition roadmap.md`. Each task above should be independently testable and deliver incremental value. Track progress in PLAN.md and update as features are completed.

