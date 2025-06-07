# Vision Alignment

All tasks and phases in this TODO are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

# Altman Z-Score TODO List (2025)

## Updated TODO List (June 2025)

### Current & Next Steps (v2.5)
- [x] Z-Score forecasting, sentiment/news analysis, and multi-ticker/portfolio support (see PLAN.md)
- [x] Modularize data connectors and enhance CLI for batch/portfolio analysis
- [x] Prepare for web dashboard, REST API, and Excel Add-In (see competition roadmap.md)

### Current & Next Steps (v2.6)
- [x] Z-Score forecasting, sentiment/news analysis, and multi-ticker/portfolio support (see PLAN.md)
- [x] Modularize data connectors and enhance CLI for batch/portfolio analysis
- [x] Prepare for web dashboard, REST API, and Excel Add-In (see competition roadmap.md)
- [x] Update all documentation and version numbers for v2.6
- [x] Tag and push v2.6 release to remote repository
- [x] Review user feedback and bug reports from v2.6
- [x] Implement improvements to LLM prompts and mapping logic based on feedback
- [ ] Plan next milestone features in PLAN.md

### Planning for v2.7
- [ ] Collect and prioritize user feedback from v2.6
- [ ] Draft v2.7 roadmap in PLAN.md

### Current & Next Steps (v2.7)
- [x] Implement robust fallback to SEC EDGAR for financials if yfinance fails
- [x] Improve error reporting for balance-sheet-only cases (e.g., TUP)
- [x] Update documentation and release checklist for v2.7
- [x] Tag and push v2.7 release to remote repository
- [ ] Collect and prioritize user feedback from v2.7
- [ ] Draft v2.8 roadmap in PLAN.md
- [ ] Expand integration and regression tests for new logic
- [ ] Continue modularization and documentation of new features

### Current & Next Steps (v2.7.1)
- [x] Update all documentation and version numbers for v2.7.1
- [x] Tag and push v2.7.1 release to remote repository
- [x] Review user feedback and bug reports from v2.7.1
- [ ] Collect and prioritize user feedback from v2.7.1

### Current & Next Steps (v2.7.3)
- [x] Codebase cleanup: removed dead code, verified all modules and prompt files are referenced and in use
- [x] Updated documentation and version numbers for v2.7.3
- [x] Modularize and refactor data_fetching/financials.py (see REFACTORING_PLAN.md for details)
- [ ] Collect and prioritize user feedback from v2.7.3
- [ ] Draft v2.8 roadmap in PLAN.md

### Current & Next Steps (v2.7.4)
- [x] Updated documentation and version numbers for v2.7.4
- [x] DRY error handling phase complete: error_helpers.py created, all custom exceptions now inherit from AltmanZScoreError, and core modules refactored to use DRY error helpers (2025-06-04)
- [ ] Collect and prioritize user feedback from v2.7.4

### Current & Next Steps (v2.9)
- [x] Verify all imports and tests after modular reorganization (core, models, company, validation, market, plotting, computation, misc)
- [x] Update documentation and README for new structure and import paths
- [ ] Continue to modularize and document new features as needed

### Current & Next Steps (v3.0)
- [x] Full modular reorganization: all code grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- [x] All imports updated to use new modular paths (e.g., from altman_zscore.plotting.plotting_main import plot_zscore_trend)
- [x] Improved LLM prompt templates and code injection for reporting: LLM commentary and report sections are now more complete, context-aware, and robust, leading to higher quality and more actionable analysis outputs
- [x] Documentation and usage examples updated to reflect new structure
- [x] All tests passing after reorganization
- [ ] Plan next milestone features in PLAN.md for v3.x

### Prompt & Mapping Tasks
- [x] All LLM prompt files are in `src/prompts/`—edit to customize LLM behavior, add new features, or update instructions
- [x] Ensure prompt changes are reflected in all outputs (test with unique phrase as described below)
- [x] Expand/normalize FIELD_SYNONYMS for all canonical fields, especially for banks and international companies
- [x] Implement sector/industry/ticker awareness in mapping logic (e.g., map 'sales' to 'Interest Income' for banks)
- [x] Allow user to provide mapping override file (e.g., mapping_overrides.json)
- [x] Add granular logging and fallback logic for mapping decisions

### Prompt Ingestion Test Checklist
1. Edit `prompt_fin_analysis.md` and add a unique phrase
2. Run the pipeline for any ticker
3. Check the output report for the phrase
4. Revert the prompt

### History (Completed/Legacy)
- v2.5: Z-Score forecasting, sentiment/news analysis, multi-ticker/portfolio support, modularized data connectors, advanced notifications, expanded documentation/testing
- v2.4: Weekly-only simplification, CLI/pipeline/docs/tests updated, dispatcher/model logic improved
- v2.3: Weekly price data overlays and pipeline integration
- v2.2.2: Script version in every report, tested companies doc, improved traceability
- v2.2: Model selection & calibration overhaul, centralized constants, industry/maturity logic
- v2.1: MVP and stock price overlay

For full roadmap and competitive tasks, see `PLAN.md` and `competition roadmap.md`.

## URGENT
- [x] Research finnhub.io and its API for potential integration (evaluate data coverage, cost, and API limits)
- [x] https://finnhub.io/docs/api
- [x] https://github.com/Finnhub-Stock-API/finnhub-python
- [x] Integrated finnhub for company profile and logo fetching (see src/altman_zscore/api/finnhub_client.py)
- [x] All code and documentation updated to reflect Finnhub integration and logo fetching

# Environment Variables

Set the following environment variables for configuration:

```bash
# Required: SEC EDGAR access
SEC_EDGAR_USER_AGENT="AltmanZScore/1.0 name@domain.com"  # Use your own contact email

# Optional: Yahoo Finance (if using premium API)
YAHOO_FINANCE_API_KEY="your-api-key"  # Do NOT share real API keys

# Optional: Finnhub (required for company profiles/logos)
FINNHUB_API_KEY="your-finnhub-api-key"  # Do NOT share real API keys
```

> **Security Note:** Never commit or share real API keys, secrets, or credentials in documentation, code, or version control. Always use placeholder values (e.g., "your-api-key") and store secrets securely using environment variables or secret managers.