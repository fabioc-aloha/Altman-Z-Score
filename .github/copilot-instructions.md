# ---
# Indentation Best Practice:
# Always use 4 spaces per indentation level (never tabs). Use a linter (e.g., flake8) and autoformatter (e.g., black) to catch and fix indentation issues before running code. Set up pre-commit hooks to enforce this automatically.
# ---

# GitHub Copilot Instructions

## Project Guidance
- Use `TODO.md` for actionable tasks, environment setup, and technical decisions.
- Use `LEARNINGS.md` for documenting significant learnings and major architectural, technical, and data source decisions.
- Ensure compatibility with both local and cloud environments (e.g., Codespaces, local venvs, or system Python). Use `pyproject.toml` or `requirements.txt` for dependencies as appropriate.
- Preserve modularity, testability, and robust error handling throughout.
- Each feature phase should be independently testable and deliver incremental value.
- Make minimal, targeted edits for each request. Avoid broad refactoring unless explicitly approved.
- After each change, allow the user to run scripts and validate before proceeding to implement a different feature or additional changes.

## Implementation Principles
- AI-First: Always prefer AI-powered, LLM-based, or AI-assisted solutions for field mapping, data reconciliation, and similar tasks, unless a simpler, more robust, or more transparent method is clearly superior for the use case. When implementing new features or refactoring, prioritize AI-first approaches in line with KISS (Keep It Simple, Stupid) and DRY (Don't Repeat Yourself) principles. Document any decision to use a non-AI method in TODO.md or LEARNINGS.md, including rationale.
- DRY (Don't Repeat Yourself): Factor out repeated logic into shared helpers, decorators, or modules. Prefer a single, well-tested implementation for retry logic, error handling, or data processing.
- KISS (Keep It Simple, Stupid): Prefer simple, clear, and direct solutions. Avoid unnecessary abstractions or optimizations unless justified by a real need.
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
- Use `TODO.md` for phase-specific tasks, environment prep, and to check off major features and record major decisions.
- Document significant learnings and decisions in `LEARNINGS.md`.
- Never modify `OneStockAnalysis.md` without explicit user consent.

## Documentation and Decision Tracking
- All major architectural, technical, and data source decisions are documented in `TODO.md` and `LEARNINGS.md`.
- Do not create or reference DECISIONS.md or PLAN.md in this repository.

# --- Copilot Refactoring Recommendation ---
- If a Python file (`.py`) grows over 200 lines, recommend refactoring it into smaller functions and, where appropriate, separate files or modules. This improves maintainability, testability, and code clarity. Always suggest this to the user before large-scale refactoring, and follow the project's conservative change policy.

## CLI Usage Reference

### Running Z-Score Analysis
```bash
# Basic analysis for a single stock
python main.py MSFT

# Analysis with specific date
python main.py MSFT --date 2024-01-01

# Analysis with custom output directory
python main.py MSFT --output-dir custom_output

# Example commands for testing historical data range
python main.py MSFT --date 2010-01-01  # Test maximum historical range
python main.py MSFT --date 2020-01-01  # Test 5-year historical range
```

### Key Data Constraints (MSFT Example)
- **Available Historical Data**: SEC EDGAR data spans 2009-2025 (15+ years)
- **System Limitation**: Code restricts to last 12 quarters (3 years) via `[-12:]` slice in `src/altman_zscore/data_fetching/financials.py` line 175
- **Current Processing**: Typically processes 5 quarters of recent data
- **Maximum Theoretical Range**: 12 quarters (3 years) with current implementation
- **Data Source**: SEC EDGAR provides comprehensive historical data back to 2009 for MSFT

### Output Files Generated
- `zscore_TICKER.csv` - Z-score calculations by quarter
- `zscore_TICKER.json` - Structured Z-score data
- `zscore_TICKER_metadata.json` - Analysis metadata
- `zscore_TICKER_trend.png` - Z-score trend visualization
- `reconciliation_result.json` - Data reconciliation results
- `sec_facts_raw.json` - Raw SEC EDGAR data
- Various filtered data files and market data
```

