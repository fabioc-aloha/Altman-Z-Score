# GitHub Copilot Instructions (2025+)

## Project Guidance
- Use `PLAN.md` for high-level features, vision, and progress tracking.
- Use `TODO.md` for actionable tasks, environment setup, and phase-specific work.
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
- Use `PLAN.md` to check off major features as they are enabled.
- Always ensure Codespaces compatibility (no local venvs, use pyproject.toml for dependencies).
- Document significant learnings in `LEARNINGS.md` and architectural decisions in `DECISIONS.md`.
- Never modify `PAPER.md` without explicit user consent.

## Testing & Quality
- All changes must pass existing and new tests.
- New features require new or updated tests.
- Documentation must be updated for new features and changes.
- Performance must be maintained or improved.

## Rollback Plan
- The previous codebase is preserved in `OLD/` and can be restored if needed.

## Conservative, Incremental Rollout Policy
- Build a minimal, robust MVP first (single-stock Z-Score trend analysis).
- Test thoroughly at each step before enabling new features.
- Only enable new features after the MVP is stable and well-tested.
- Light up features one at a time, with tests and documentation, to avoid regressions.
- Avoid over-ambitious changes; prioritize reliability and maintainability.

## Archival of Previous Version
- The previous codebase, including all legacy scripts, tests, and documentation, is now in the `OLD/` directory for reference and rollback only.
- All new Copilot suggestions and code generation should target the new project structure and requirements.

---

