# GitHub Copilot Instructions - Altman Z-Score Refactoring

## Code Standards
- **Indentation**: 4 spaces per level (never tabs)
- **File Size**: <200 lines per file, <50 lines per function
- **Single Responsibility**: One purpose per class/function/module

## Architecture (Refactored)
- **Legacy Code**: `src/altman_zscore/` (read-only reference)
- **New Code**: `altman_zscore/` (modular layered architecture)
- **Import Rule**: Any `src.altman_zscore.*` import indicates legacy dependency

## Layer Structure
1. **Layer 0**: Field Mapping Cache (deterministic, pre-built)
2. **Layer 1**: Data Fetch (SEC + Yahoo, deterministic, no AI)
3. **Layer 2**: Field Mapping (AI/LLM allowed here only)
4. **Layer 3**: Model Selection (rule-based)
5. **Layer 4**: Z-Score Calculation (strict theory adherence)
6. **Layer 5**: Market Data (Yahoo Finance only)
7. **Layer 6**: Output Generation (CSV, JSON, charts, reports)

## Key Rules
- **Deterministic Data Fetch**: No AI/LLM in data fetch layer
- **Data Source Separation**: SEC (financials) vs Yahoo (market data)
- **API Rate Limiting**: Use `rate_limiter` for all external API calls
- **Cross-Reference Docs**: MODELS.md, APIS.md, FLOW.md, REFACTORING_PLAN.md

## Implementation
- Follow REFACTORING_PLAN.md phases
- Create comprehensive unit tests for each layer
- Use data models from `altman_zscore/models/data_models.py`
- Apply rate limiting with `@rate_limiter.rate_limited("domain")`

## Documentation
- **CHANGELOG.md**: Completed work
- **FLOW.md**: Current architecture  
- **TODO.md**: Planned work
