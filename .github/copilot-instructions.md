# ---
# Indentation Best Practice:
# Always use 4 spaces per indentation level (never tabs). Use a linter (e.g., flake8) and autoformatter (e.g., black) to catch and fix indentation issues before running code. Set up pre-commit hooks to enforce this automatically.
# ---

# GitHub Copilot Instructions

## Project Guidance
- Use `PLAN.md` for high-level features, vision, progress tracking, and major architectural/technical decisions.
- Use `TODO.md` for actionable tasks, environment setup, and technical decisions.
- Development and testing may be performed in local or cloud environments—ensure compatibility across common setups.
- Preserve modularity, testability, and robust error handling throughout.
- Each feature phase should be independently testable and deliver incremental value.
- Be conservative in implementing changes: make minimal, targeted edits for each request, and avoid broad refactoring unless explicitly approved.
- After each change, allow the user to run scripts and validate before proceeding to implement a different feature or additional changes.

## Implementation Principles
- Simplicity: Start with a single-stock analysis pipeline, then generalize to portfolios.
- Modularity: Clean separation of data fetching, validation, computation, and reporting.
- Testability: Each module is independently testable with clear interfaces.
- Robustness: Strong error handling, logging, and data validation at every step.
- Extensibility: Easy to add new data sources, models, or output formats.

## Architecture Overview
1. Input Layer: Accepts ticker(s) and analysis date; validates input.
2. Data Fetching Layer: Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance).
3. Validation Layer: Validates raw data using Pydantic schemas; reports missing/invalid fields.
4. Computation Layer: Computes Altman Z-Score using validated data; returns result object.
5. Reporting Layer: Outputs results to CSV, JSON, or stdout; logs all steps and errors.

## Workflow
- Use `TODO.md` for phase-specific tasks and environment prep.
- Use `PLAN.md` to check off major features and record major decisions.
- Ensure compatibility with both local and cloud environments (e.g., Codespaces, local venvs, or system Python). Use `pyproject.toml` or `requirements.txt` for dependencies as appropriate.
- Document significant learnings in `LEARNINGS.md`.
- Never modify `OneStockAnalysis.md` without explicit user consent.

## Documentation and Decision Tracking
- All major architectural, technical, and data source decisions are documented in PLAN.md and TODO.md.
- Do not create or reference DECISIONS.md in this repository.

# --- Copilot Refactoring Recommendation ---
- If a Python file (`.py`) grows over 200 lines, recommend refactoring it into smaller functions and, where appropriate, separate files or modules. This improves maintainability, testability, and code clarity. Always suggest this to the user before large-scale refactoring, and follow the project's conservative change policy.
# ---

