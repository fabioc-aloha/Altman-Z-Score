# Vision Alignment

All tasks and phases in this TODO are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

# Altman Z-Score TODO List (2025)

## Current & Next Steps (v2.4+)
- [ ] Add warnings for size/leverage outliers in the report
- [ ] Expand unit/integration tests for new model selection and reporting logic
- [ ] Integrate additional industry benchmark data (WRDS/Compustat or open data) into constants.py as available
- [ ] Document and automate calibration update process in altmans.md
- [ ] Schedule periodic calibration updates and document the process
- [ ] Continue to refine transparency and reporting for edge cases
- [ ] Z-Score forecasting, sentiment/news analysis, and multi-ticker/portfolio support (see PLAN.md)
- [ ] Expand FIELD_SYNONYMS and mapping logic for international/bank tickers (add multi-language, sector-aware mapping, and user overrides)
- [ ] Add/expand tests for prompt ingestion, mapping, and reporting
- [ ] Improve documentation for mapping, prompt usage, and internationalization
- [ ] Modularize data connectors and enhance CLI for batch/portfolio analysis
- [ ] Prepare for web dashboard, REST API, and Excel Add-In (see competition roadmap.md)

## Prompt & Mapping Tasks
- [ ] All LLM prompt files are in `src/prompts/`—edit to customize LLM behavior, add new features, or update instructions
- [ ] Ensure prompt changes are reflected in all outputs (test with unique phrase as described below)
- [ ] Expand/normalize FIELD_SYNONYMS for all canonical fields, especially for banks and international companies
- [ ] Implement sector/industry/ticker awareness in mapping logic (e.g., map 'sales' to 'Interest Income' for banks)
- [ ] Allow user to provide mapping override file (e.g., mapping_overrides.json)
- [ ] Add granular logging and fallback logic for mapping decisions

## Prompt Ingestion Test Checklist
1. Edit `prompt_fin_analysis.md` and add a unique phrase
2. Run the pipeline for any ticker
3. Check the output report for the phrase
4. Revert the prompt

## History (Completed/Legacy)
- v2.4: Weekly-only simplification, CLI/pipeline/docs/tests updated, dispatcher/model logic improved
- v2.3: Weekly price data overlays and pipeline integration
- v2.2.2: Script version in every report, tested companies doc, improved traceability
- v2.2: Model selection & calibration overhaul, centralized constants, industry/maturity logic
- v2.1: MVP and stock price overlay

For full roadmap and competitive tasks, see `PLAN.md` and `competition roadmap.md`.

