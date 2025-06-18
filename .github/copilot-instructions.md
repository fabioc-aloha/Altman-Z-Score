# ---
# Indentation Best Practice:
# Always use 4 spaces per indentation level (never tabs). Use a linter (e.g., flake8) and autoformatter (e.g., black) to catch and fix indentation issues before running code. Set up pre-commit hooks to enforce this automatically.
# ---

# GitHub Copilot Instructions

## Documentation Strategy
- **Past**: `CHANGELOG.md` - Documents completed features, bug fixes, and version history
- **Present**: `FLOW.md` - Documents current system architecture, data flow, and operational workflow  
- **Future**: `TODO.md` - Documents planned features, priorities, and actionable tasks
- Keep each file focused on its time perspective and cross-reference between them

## Project Guidance
- Use `TODO.md` for actionable tasks, environment setup, and technical decisions.
- Ensure compatibility with both local and cloud environments (e.g., Codespaces, local venvs, or system Python). Use `pyproject.toml` or `requirements.txt` for dependencies as appropriate.
- Preserve modularity, testability, and robust error handling throughout.
- Each feature phase should be independently testable and deliver incremental value.
- Make minimal, targeted edits for each request. Avoid broad refactoring unless explicitly approved.
- After each change, allow the user to run scripts and validate before proceeding to implement a different feature or additional changes.

## Implementation Principles
- AI-First: Always prefer AI-powered, LLM-based, or AI-assisted solutions for field mapping, data reconciliation, and similar tasks, unless a simpler, more robust, or more transparent method is clearly superior for the use case. When implementing new features or refactoring, prioritize AI-first approaches in line with KISS (Keep It Simple, Stupid) and DRY (Don't Repeat Yourself) principles. 
- DRY (Don't Repeat Yourself): Factor out repeated logic into shared helpers, decorators, or modules. Prefer a single, well-tested implementation for retry logic, error handling, or data processing.
- KISS (Keep It Simple, Stupid): Prefer simple, clear, and direct solutions. Avoid unnecessary abstractions or optimizations unless justified by a real need.
- Simplicity: Start with a single-stock analysis pipeline, then generalize to portfolios.
- Modularity: Clean separation of data fetching, validation, computation, and reporting.
- Testability: Each module is independently testable with clear interfaces.
- Robustness: Strong error handling, logging, and data validation at every step.
- Extensibility: Easy to add new data sources, models, or output formats.
- Documentation: Use docstrings, comments, and markdown files to explain complex logic, decisions, and usage.
- Version Control: Use Git branches for each feature or bug fix. Follow a clear commit message format (e.g., "feat: add new data source", "fix: resolve issue with data validation").
