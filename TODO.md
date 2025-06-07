# Vision Alignment

All tasks and phases in this TODO are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

# Altman Z-Score TODO List (2025)

## v3.0.0 Release Status ✅ FULLY COMPLETED

**All modularization work is complete and tested.**

- [x] **✅ Full modular reorganization:** All code grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- [x] **✅ All imports updated:** Use new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`)
- [x] **✅ Integration testing:** Added `tests/test_integration_main.py` to catch import/runtime errors
- [x] **✅ Critical import fixes:** Resolved all ModuleNotFoundError issues in fetcher_factory.py, industry_classifier.py, etc.
- [x] **✅ Main pipeline verified:** Successfully runs `python main.py msft` without import errors
- [x] **✅ Improved LLM prompt templates:** Enhanced code injection for reporting with better analysis outputs
- [x] **✅ Documentation updated:** All documentation reflects new structure and completed modularization
- [x] **✅ All tests passing:** Both unit tests and integration tests pass after reorganization
- [x] **✅ Modularization & refactoring complete:** All refactoring work finished and tested

## Current Phase: v3.0 Production Deployment

### Immediate Next Steps
- [ ] **🚀 Deploy v3.0 for practical use:** Begin using the modularized codebase in real-world scenarios
- [ ] **📊 Collect user feedback:** Gather feedback on the new modular structure, import paths, and overall usability
- [ ] **📈 Monitor performance:** Track any performance impacts from the modularization
- [ ] **🔍 Identify pain points:** Document any issues users encounter with the new structure
- [ ] **📝 Document learnings:** Record insights from practical usage in LEARNINGS.md

### v3.1 Planning
- [ ] Analyze collected user feedback from v3.0 practical use
- [ ] Prioritize feedback-driven improvements and bug fixes
- [ ] Draft v3.1 roadmap in PLAN.md based on user needs
- [ ] Plan next milestone features for v3.x series

## Future Development Roadmap (v3.1+)

**Note:** These are potential features to consider based on user feedback and competitive analysis. Prioritization will be based on practical usage insights from v3.0 deployment.

### Performance & Scalability
- [ ] Performance optimization based on practical usage patterns
- [ ] Caching strategies for frequently analyzed tickers
- [ ] Batch processing optimizations for large portfolios
- [ ] Memory usage optimization for large datasets

### User Experience Enhancements
- [ ] Enhanced CLI with interactive mode
- [ ] Real-time analysis dashboard (web interface)
- [ ] Export formats (Excel, PowerBI, etc.)
- [ ] Email/notification system for alerts

### Data & Analysis Enhancements
- [ ] Additional financial models beyond Altman Z-Score
- [ ] International company support improvements
- [ ] Industry-specific model calibrations
- [ ] Advanced forecasting capabilities

### Integration & API Features
- [ ] REST API for programmatic access
- [ ] Database backend for historical data storage
- [ ] Third-party tool integrations
- [ ] Excel Add-In development

## Technical Maintenance

### Prompt & LLM Customization
- [x] All LLM prompt files are in `src/prompts/`—edit to customize LLM behavior, add new features, or update instructions
- [x] Ensure prompt changes are reflected in all outputs (test with unique phrase as described below)
- [x] Expand/normalize FIELD_SYNONYMS for all canonical fields, especially for banks and international companies
- [x] Implement sector/industry/ticker awareness in mapping logic (e.g., map 'sales' to 'Interest Income' for banks)
- [x] Allow user to provide mapping override file (e.g., mapping_overrides.json)
- [x] Add granular logging and fallback logic for mapping decisions

#### Prompt Testing Workflow
1. Edit `prompt_fin_analysis.md` and add a unique phrase
2. Run the pipeline for any ticker
3. Check the output report for the phrase
4. Revert the prompt

### API Integrations
#### Finnhub Integration ✅ COMPLETED
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