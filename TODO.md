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

