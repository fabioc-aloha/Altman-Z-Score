# Refactoring Plan: Modularization & Function Decomposition

## Guidelines
- Do NOT add new features or remove existing features during refactoring.
- Do NOT introduce regressions—ensure all existing tests pass and all current functionality is preserved.
- Refactoring should be limited to code structure, modularity, and readability improvements only.
- All interfaces, APIs, and outputs must remain unchanged unless strictly necessary for modularization (and must be documented if so).
- Use incremental, testable changes and validate after each major step.

## Goals
- Break up any Python file over 300 lines into smaller, focused modules.
- Refactor long functions into smaller, testable units.
- Improve readability, maintainability, and testability.
- Preserve all existing functionality and interfaces.
- Update imports and documentation as needed.

---

## Checklist

### 1. Audit & Inventory
- [ ] List all Python files and their line counts.
- [ ] Identify files > 300 lines.
- [ ] Identify functions > 50 lines (or otherwise complex/monolithic).

### 2. Refactoring Strategy
- [ ] For each large file, propose logical module boundaries (e.g., split by feature, class, or responsibility).
- [ ] For each long function, outline how to break it into smaller helper functions or methods.
- [ ] Ensure each new module/file is independently testable.

### 3. Implementation
- [ ] Create new modules/files as needed.
- [ ] Move code into new files, updating imports and references.
- [ ] Refactor long functions into smaller units.
- [ ] Add or update docstrings and comments for clarity.
- [ ] Update or add tests for new modules/functions.
- [ ] Create or update unit tests for all new/refactored modules/functions to cover critical paths and edge cases.

### 4. Validation
- [ ] Run all tests and validation scripts; ensure all pass.
- [ ] Manually review for duplicate code, dead code, or missed imports.
- [ ] Check that all documentation and usage examples are up to date.

### 5. Documentation & Changelog
- [ ] Update `CHANGELOG.md` to summarize refactoring and module changes.
- [ ] Update `README.md` and any relevant docs to reflect new module structure.
- [ ] Note any major architectural decisions in `PLAN.md`.

### 6. Git & Release
- [ ] Stage, commit, and push all changes.
- [ ] Tag the refactored release (e.g., v2.8.0 or similar).

---

## Codebase Audit Results (June 2025)

The following files in `src/` exceed 300 lines and are strong candidates for modularization and function decomposition:

- data_fetching/financials.py (582 lines)
- company_profile.py (454 lines)
- company_status.py (305 lines)
- one_stock_analysis.py (397 lines)
- plotting.py (504 lines)
- reporting.py (370 lines)
- api/openai_client.py (370 lines)
- zscore_models.py (327 lines)
- plot_blocks.py, plot_helpers.py, computation/formulas.py, and others are also large and should be reviewed.

Many other files are between 100–300 lines and may also benefit from function decomposition.

### Plan Realism
- The current plan is realistic and directly applicable to the codebase.
- Multiple files and likely functions exceed best-practice size limits.
- Refactoring will improve maintainability, testability, and clarity.

### Next Steps
- Identify the largest/most complex functions in these large files.
- Propose module boundaries and function splits for each large file.
- Proceed with the checklist steps for each file, starting with the largest or most critical modules.

This plan is complete and ready for use. Proceed to the audit and inventory step to begin the refactoring process.

---

## Per-File Refactoring Checklists (with Function Inventory)

### data_fetching/financials.py (before: 582 lines, after: 365 lines)
- [x] Inventory all functions and classes
    - df_to_dict_str_keys
    - find_matching_field
    - find_xbrl_tag
    - fetch_sec_edgar_data
    - fetch_financials
    - fetch_company_officers
    - fetch_executive_data
- [x] Identify functions > 50 lines (e.g., fetch_financials, fetch_executive_data)
- [x] Propose module boundaries (e.g., split by data source, validation, helpers)
- [x] Refactor long functions into smaller units (where possible)
- [x] Move code into new modules/files as needed
- [x] Update imports and references
- [x] Add/Update tests
- [x] Validate and document changes

### company_profile.py (before: 454 lines, after: much smaller; all business logic moved to helpers)
- [x] Inventory all functions and classes
    - __init__
    - classify_maturity
    - from_ticker
    - find_field (moved)
    - __str__
    - lookup_cik
    - classify_company_by_sec (moved)
- [x] Identify functions > 50 lines
    - from_ticker
    - classify_company_by_sec
- [x] Propose module boundaries (e.g., profile fetch, parsing, formatting)
    - profile fetch: from_ticker, lookup_cik
    - parsing: find_field (moved), classify_company_by_sec (moved)
    - formatting: __str__, classify_maturity
- [x] Refactor long functions into smaller units
    - Split `from_ticker` and `classify_company_by_sec` into logical helpers for modularity and clarity
- [x] Move code into new modules/files as needed
    - All business logic and helpers moved to company_profile_helpers.py
- [x] Update imports and references
- [x] Add/Update tests
- [x] Validate and document changes

### company_status.py (305 lines)
- [x] Inventory all functions and classes
    - __init__
    - to_dict
    - get_status_message
    - check_company_status
    - detect_company_region
    - handle_special_status
- [x] Identify functions > 50 lines (e.g., check_company_status)
- [x] Propose module boundaries
    - status computation: check_company_status, handle_special_status
    - region detection: detect_company_region
    - serialization/representation: to_dict, get_status_message
    - class definition/init: __init__
- [x] Refactor long functions into smaller units
    - Broke up check_company_status and handle_special_status for clarity and modularity
- [x] Move code into new modules/files as needed
    - Moved business logic and helpers to company_status_helpers.py
- [x] Update imports and references
    - Updated all usages to import from helpers
- [x] Add/Update tests
    - Added tests for check_company_status, handle_special_status, detect_company_region
    - Patched file outputs for testability
- [x] Validate and document changes
    - All tests pass, Pylance errors resolved, and debug output removed

### one_stock_analysis.py (397 lines)
- [ ] Inventory all functions and classes
    - print_info
    - print_success
    - print_warning
    - print_error
    - print_header
    - get_zscore_path
    - check_company_status
    - classify_and_prepare_output
    - filter_valid_quarters
    - analyze_single_stock_zscore_trend
    - safe_payload (nested)
- [ ] Identify functions > 50 lines (e.g., analyze_single_stock_zscore_trend)
- [ ] Propose module boundaries (e.g., input, analysis, reporting)
- [ ] Refactor long functions into smaller units
- [ ] Move code into new modules/files as needed
- [ ] Update imports and references
- [ ] Add/Update tests
- [ ] Validate and document changes

### plotting.py (504 lines -> ~300 lines)
- [x] Inventory all functions and classes
    - Colors (moved)
    - print_info (moved)
    - print_warning (moved)
    - print_error (moved)
    - get_output_ticker_dir
    - get_zscore_thresholds
    - plot_zscore_trend
    - plot_zscore_trend_pipeline
- [x] Identify functions > 50 lines
    - plot_zscore_trend (~170 lines)
    - plot_zscore_trend_pipeline (~200 lines)
- [x] Propose module boundaries
    - Terminal output helpers: Colors, print_info/warning/error -> plotting_terminal.py
    - Plot formatting helpers: band/label/legend generation -> plotting_helpers.py
    - Main plotting logic: plot_zscore_trend, plot_zscore_trend_pipeline
- [x] Refactor long functions into smaller units
    - Extracted make_zone_bands, add_zone_labels from plot functions
    - Extracted make_legend_elements, save_plot_with_legend for reusability
    - Reduced duplication between plot_zscore_trend and plot_zscore_trend_pipeline
- [x] Move code into new modules/files as needed
    - Created plotting_terminal.py for all terminal output helpers
    - Created plotting_helpers.py for matplotlib formatting helpers
- [x] Update imports and references
    - Updated plotting.py to use new helper modules
    - Adjusted figure dimensions for better layout
- [x] Add/Update tests for plotting_terminal.py
    - Created test_plotting_terminal.py with full test coverage
    - Added tests for Colors class attributes
    - Added tests for color output functionality
    - Added tests for fallback behavior when color not supported
    - Fixed test failures and improved test reliability
- [x] Add/Update tests for plotting_helpers.py
    - test_plotting_helpers.py covers all helper functions
    - Includes tests for make_zone_bands (normal, edge, error cases)
    - Includes tests for add_zone_labels (normal, edge, error cases)
    - Includes tests for make_legend_elements (labels, colors, structure)
    - Includes tests for save_plot_with_legend (file output)
    - All tests pass in headless and CI environments
- [x] Validate and document changes
    - Docstrings updated in plotting_helpers.py
    - Usage examples added in comments
    - Figure dimensions verified across all test cases

### reporting.py (370 lines)
- [ ] Inventory all functions and classes
    - print_info
    - report_zscore_full_report
    - format_number_millions (nested)
- [ ] Identify functions > 50 lines (e.g., report_zscore_full_report)
- [ ] Propose module boundaries (e.g., output, formatting, helpers)
- [ ] Refactor long functions into smaller units
- [ ] Move code into new modules/files as needed
- [ ] Update imports and references
- [ ] Add/Update tests
- [ ] Validate and document changes

### api/openai_client.py (370 lines)
- [ ] Inventory all functions and classes
    - __init__
    - chat_completion
    - suggest_field_mapping
    - _extract_trimmed_sec_info
    - _extract_trimmed_company_info
    - get_llm_qualitative_commentary
- [ ] Identify functions > 50 lines (e.g., suggest_field_mapping, get_llm_qualitative_commentary)
- [ ] Propose module boundaries (e.g., client, helpers, config)
- [ ] Refactor long functions into smaller units
- [ ] Move code into new modules/files as needed
- [ ] Update imports and references
- [ ] Add/Update tests
- [ ] Validate and document changes

### zscore_models.py (327 lines)
- [ ] Inventory all functions and classes (see grep results for full list)
- [ ] Identify functions > 50 lines
- [ ] Propose module boundaries (e.g., model definitions, utilities)
- [ ] Refactor long functions into smaller units
- [ ] Move code into new modules/files as needed
- [ ] Update imports and references
- [ ] Add/Update tests
- [ ] Validate and document changes

### plot_blocks.py, plot_helpers.py, computation/formulas.py, etc.
- [ ] Review file size and complexity
- [ ] Apply above checklist as needed
