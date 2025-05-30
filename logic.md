# Vision Alignment

All logic and architectural decisions are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

# Codebase Review: Logic Duplication, Conflicts, and Refactor Plan

## 1. Logic Duplication & Conflicts
- **Z-Score Model Formulas:** Duplicate implementations exist in both `compute_zscore.py` and `computation/formulas.py`. This risks inconsistencies and complicates maintenance.
- **Model Selection Logic:** Model selection and threshold logic are repeated in several places. This should be centralized.
- **Safe Division & Error Handling:** The `safe_div` function and division-by-zero checks are present in multiple modules. This logic should be unified.
- **Validation Layer:** The `FinancialDataValidator` class has both `validate` and `validate_data` as aliases. Ensure only one is used in the pipeline for clarity.
- **Threshold Definitions:** Safe/distress zone thresholds are duplicated across model implementations. These should be centralized.
- **Validation Rules:** Overlap between validation rules in `api/base_fetcher.py` and `data_validation.py` needs consolidation.

## 2. Error Handling & Robustness
- **Exception Handling:** Some modules use broad `except Exception:` blocks. Replace with more specific exception handling and logging.
- **Network Resilience:** Data fetching modules need unified retry logic, better diagnostics, and fallback strategies.
- **Input Validation:** Input validation could be more robust, especially for date and ticker formats.
- **Market Calendar Integration:** Missing proper handling of market holidays and non-trading days.
- **Data Source Fallbacks:** Need more robust fallback strategies when primary data sources are unavailable.
- **Model Initialization:** Model caching and initialization in `models/base.py` needs better error handling.

## 3. Modularity & Testability
- **Large Functions:** Functions like `analyze_single_stock_zscore_trend` are too large and should be broken down for testability.
- **Logging:** There is a mix of print statements and logging. Standardize on the Python logging module.
- **Date Handling:** Date alignment and formatting logic is scattered and inconsistent.

## 4. Documentation & Consistency
- **Docstrings:** Some functions lack clear docstrings, especially in plotting and data fetching modules.
- **Environment Variables:** Validation for required environment variables is not always performed early.

---

## Consolidated Refactor Plan

### A. Centralize & Deduplicate
- [ ] Remove all formula implementations from `compute_zscore.py` and import exclusively from `computation/formulas.py`.
- [ ] Centralize thresholds and model mappings (industry, maturity, safe/distress) in `computation/model_selection.py` or a dedicated `constants.py`.
- [ ] Consolidate `safe_div` and division-by-zero checks into `utils/financial_metrics.py`.

### B. Data Layer & Resilience
- [ ] Integrate a market-holiday calendar (e.g., via `pandas_market_calendars`) and fallback to prior trading day.
- [ ] Implement a `CacheManager` in `utils/cache.py` to persist and reuse fetcher results.
- [ ] Consolidate overlapping validation rules between `api/base_fetcher.py` and `schemas/validation.py`.
- [ ] Enhance retry/backoff and fallback logic in all data fetchers (`api/*`, `data_fetching/*`).

### C. Error Handling & Logging
- [ ] Replace broad `except Exception:` blocks with specific exception catches and include detailed logging.
- [ ] Centralize logging configuration in `utils/logging.py` and initialize in `main.py`.
- [ ] Add fail-fast checks for required environment variables (SEC_EDGAR_USER_AGENT, NEWSAPI_KEY, etc.).

### D. Modularity & Testing
- [ ] Break down large functions (e.g., `analyze_single_stock_zscore_trend`, plotting routines) into focused, testable units.
- [ ] Centralize date parsing and alignment in `utils/time_series.py`.
- [ ] Expand test coverage:
  - Unit tests for model selection, `safe_div`, date utilities, cache manager.
  - Integration tests for full pipeline with mocked API responses.
  - Edge case tests: industry model mapping, holiday/non-trading days.
  - Performance benchmarks for data fetching routines.

### E. Documentation & Consistency
- [ ] Audit and add docstrings for every public function (parameters, returns, exceptions).
- [ ] Update `README.md`, `PLAN.md`, `TODO*.md` to reflect single entry point `main.py`, remove legacy references.
- [ ] Standardize naming conventions (Z-Score vs ZScore) and markdown formatting across docs.

---

**Next Steps (priority order):**
1. Centralize model logic and remove formula duplication.
2. Implement market-calendar integration and caching.
3. Configure centralized logging and env-var validation.
4. Refactor large modules and expand unit tests.
5. Consolidate validation rules and complete integration tests.
