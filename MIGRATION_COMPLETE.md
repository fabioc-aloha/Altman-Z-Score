# HTML Output Directory Migration Complete

## Summary
Successfully migrated the HTML generator system to use the `web/` directory instead of `output/` for all generated HTML files.

## Changes Made

### 1. Core Portfolio Generation System
- **File**: `altman_zscore/portfolio_generation/base.py`
  - Updated `PortfolioGenerator.__init__()` to use `web/` directory for HTML output
  - Changed: `HTMLPortfolioGenerator(output_base_dir)` → `HTMLPortfolioGenerator(os.path.join(output_base_dir, "web"))`

### 2. HTML Generator
- **File**: `altman_zscore/portfolio_generation/html_generator.py`
  - Added automatic directory creation in `__init__()` method
  - Ensures `web/` directory is created if it doesn't exist

### 3. Portfolio Generation Script
- **File**: `altman_zscore/scripts/generate_portfolio.py`
  - Updated `PortfolioGeneratorScript.__init__()` to create and manage `web/` directory
  - Added logging to indicate HTML files will be generated in `web/`

### 4. Main Page Generator
- **File**: `generate_main_page.py`
  - Changed output path from `index.html` to `web/index.html`
  - Updated dashboard detection to look for files in `web/` directory
  - Added automatic `web/` directory creation

### 5. Model Portfolios Generator
- **File**: `generate_model_portfolios.py`
  - Updated output directory from `.` to `./web`
  - Changed main index file path to `web/model_portfolios_index.html`

### 6. Documentation Updates
- **File**: `docs/table.md`
  - Updated all relative paths from `output/` to `../output/` since table is now in `docs/`
  - All company report links now work correctly from the docs directory

## File Migration
- Moved all existing HTML files from project root to `web/` directory:
  - `index.html` → `web/index.html`
  - `strong_buys.html` → `web/strong_buys.html`
  - `value_picks.html` → `web/value_picks.html`
  - `growth_picks.html` → `web/growth_picks.html`
  - `aggressive_picks.html` → `web/aggressive_picks.html`
  - `conservative_picks.html` → `web/conservative_picks.html`
  - `dividend_picks.html` → `web/dividend_picks.html`
  - `sell_picks.html` → `web/sell_picks.html`
  - `strong_sell_picks.html` → `web/strong_sell_picks.html`
  - `test_portfolio.html` → `web/test_portfolio.html`

## Directory Structure
```
project-root/
├── web/                           # NEW: All HTML files
│   ├── index.html                 # Main navigation
│   ├── strong_buys.html           # Portfolio dashboards
│   ├── value_picks.html
│   ├── growth_picks.html
│   ├── aggressive_picks.html
│   ├── conservative_picks.html
│   ├── dividend_picks.html
│   ├── sell_picks.html
│   ├── strong_sell_picks.html
│   ├── model_portfolios_index.html
│   ├── manufacturing_&_industrial.html
│   ├── private_&_service_companies.html
│   ├── emerging_markets.html
│   ├── financial_institutions.html
│   ├── regulated_utilities.html
│   ├── technology_&_growth.html
│   ├── retail_&_consumer.html
│   └── *.css                      # Associated CSS files
├── output/                        # Company analysis data (unchanged)
│   └── COMPANY_SYMBOL/
│       ├── comprehensive_report.html
│       └── company_logo.png
└── docs/                          # Documentation (unchanged)
    └── table.md                   # Updated with correct relative paths
```

## Testing
✅ Portfolio generation: All portfolio types generate correctly in `web/`
✅ Main page generation: Creates `web/index.html` successfully
✅ Model portfolios: Creates files in `web/` directory
✅ File access: All HTML files open correctly in browser
✅ Clean root: No HTML files remain in project root

## Impact
- **HTML Output**: All new HTML files are now created in `web/` directory
- **Data Files**: Company analysis data remains in `output/` directory (unchanged)
- **Documentation**: All documentation files moved to `docs/` directory
- **Clean Structure**: Project root is now clean with only essential code files

## Commands to Test
```bash
# Generate individual portfolio
python -m altman_zscore.scripts.generate_portfolio strong_buy

# Generate all portfolios
python -m altman_zscore.scripts.generate_portfolio all

# Generate main navigation page
python generate_main_page.py

# Generate model-specific portfolios
python generate_model_portfolios.py
```

All HTML output is now properly organized in the `web/` directory!

## Test Scripts Organization

### Completed: Test Files Moved to `tests/` Directory
- **Integration Tests**: Moved to `tests/integration/`
  - `test_consolidated_portfolio_system.py`
  - `test_ai_integration.py` 
  - `test_ai_pipeline.py`
- **Unit Tests**: Moved to `tests/unit/`
  - `test_html_generator.py`
  - `test_modular_portfolio_system.py`
  - `test_modular_charts.py`
- **Basic Tests**: Moved to `tests/`
  - `test_basic_ai.py`

### Import Path Updates
- Fixed all import paths to work from new locations
- Updated HTML generator test to use `web/` directory
- All tests now run correctly from organized structure

### Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run individual test scripts
python tests/test_basic_ai.py
python tests/unit/test_html_generator.py
python tests/integration/test_consolidated_portfolio_system.py
```

See `TEST_ORGANIZATION_COMPLETE.md` for detailed information.
