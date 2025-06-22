# Scripts Directory

This directory contains utility scripts, exploration tools, and debugging scripts for the Altman Z-Score project.

## Structure

### `exploration/` - Development & Debugging Scripts
Scripts used for API exploration, debugging, and proof-of-concept development:

- `fmp_api_explorer.py` - Financial Modeling Prep API exploration
- `fmp_estimates_explorer.py` - FMP estimates data exploration
- `fmp_estimates_explorer_fixed.py` - Fixed version of estimates explorer
- `debug_fmp_ratios.py` - Debug FMP ratios data
- `debug_imports.py` - Import debugging utility
- `api_caching_demo.py` - API caching demonstration
- `llm_demo.py` - LLM integration demonstration

### `utilities/` - Build & Maintenance Scripts
Production utility scripts for building, testing, and maintenance:

- `build_field_database.py` - Build field mapping database
- `generate_readme_table.py` - Generate portfolio analysis table
- `analyze_fmp_tiers.py` - Analyze FMP subscription tiers
- `verify_improvements.py` - Verify system improvements
- `run_tests.py` - Legacy test runner (replaced by root `run_organized_tests.py`)

## Usage

Most scripts can be run directly from the project root:

```bash
# Exploration scripts
python scripts/exploration/fmp_api_explorer.py
python scripts/exploration/api_caching_demo.py

# Utility scripts  
python scripts/utilities/generate_readme_table.py
python scripts/utilities/build_field_database.py
```

## Path Configuration

Scripts that import project modules should include path configuration:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
```

**Note:** For new development, use the organized test structure in `tests/` and the main application entry point `main.py`.
