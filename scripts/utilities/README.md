# Dashboard Generation Utilities

This directory contains the Python scripts used by the main PowerShell dashboard generator.

## Scripts

- `generate_portfolio_modern.py` - Generates portfolio dashboards for different investor types (strong buy, value, growth, dividend, conservative, aggressive, sell, strong sell)
- `generate_model_portfolios.py` - Generates model-specific portfolios (emerging markets, manufacturing & industrial, etc.)
- `generate_main_page.py` - Generates the main navigation page that links to all dashboards

## Usage

These scripts are typically called from the root PowerShell script `generate_all_dashboards_improved.ps1`, but can also be run directly:

```
# Generate a specific portfolio dashboard
python scripts/utilities/generate_portfolio_modern.py strong_buy

# Generate all portfolio dashboards
python scripts/utilities/generate_portfolio_modern.py all

# Generate model portfolios
python scripts/utilities/generate_model_portfolios.py

# Generate the main navigation page
python scripts/utilities/generate_main_page.py
```

All HTML output is written to the `/web` directory in the project root.
