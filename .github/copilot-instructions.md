# GitHub Copilot Instructions (2025+)

## Project Guidance
- Use `PLAN.md` for high-level features, vision, progress tracking, and major architectural/technical decisions.
- Use `TODO.md` for actionable tasks, environment setup, phase-specific work, and technical decisions.
- All development and testing is performed in GitHub Codespaces—ensure compatibility at every step.
- Preserve modularity, testability, and robust error handling throughout.
- Each feature phase should be independently testable and deliver incremental value.

## Feature Roadmap (see PLAN.md for details)
- [x] MVP: Single-Stock Z-Score Trend Analysis
- [ ] v1: Overlay Stock Price Trend
- [ ] v2: Sentiment & News Analysis
- [ ] v3: Portfolio Analysis
- [ ] v4: Advanced Correlation & Insights

## Implementation Principles
- **Simplicity:** Start with a single-stock analysis pipeline, then generalize to portfolios.
- **Modularity:** Clean separation of data fetching, validation, computation, and reporting.
- **Testability:** Each module is independently testable with clear interfaces.
- **Robustness:** Strong error handling, logging, and data validation at every step.
- **Extensibility:** Easy to add new data sources, models, or output formats.

## Architecture Overview
1. **Input Layer**: Accepts ticker(s) and analysis date; validates input.
2. **Data Fetching Layer**: Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance).
3. **Validation Layer**: Validates raw data using Pydantic schemas; reports missing/invalid fields.
4. **Computation Layer**: Computes Altman Z-Score using validated data; returns result object.
5. **Reporting Layer**: Outputs results to CSV, JSON, or stdout; logs all steps and errors.

## Workflow
- Use `TODO.md` for phase-specific tasks (e.g., scaffolding, environment prep, feature implementation).
- Use `PLAN.md` to check off major features as they are enabled and to record all major decisions.
- Always ensure Codespaces compatibility (no local venvs, use pyproject.toml for dependencies).
- Document significant learnings in `LEARNINGS.md`.
- Never modify `OneStockAnalysis.md` without explicit user consent.

## Testing & Quality
- All changes must pass existing and new tests.
- New features require new or updated tests.
- Documentation must be updated for new features and changes.
- Performance must be maintained or improved.

## Rollback Plan
- If a rollback is needed, restore from version control (git history).

## Conservative, Incremental Rollout Policy
- Build a minimal, robust MVP first (single-stock Z-Score trend analysis).
- Test thoroughly at each step before enabling new features.
- Only enable new features after the MVP is stable and well-tested.
- Light up features one at a time, with tests and documentation, to avoid regressions.
- Avoid over-ambitious changes; prioritize reliability and maintainability.

## Documentation and Decision Tracking Update (May 23, 2025)
- The DECISIONS.md file has been removed from the repository.
- All major architectural, technical, and data source decisions are now documented in PLAN.md and TODO.md.
- Do not create or reference DECISIONS.md in this repository.

---

