# Altman-Z-Score

## Overview
This tool analyzes YTD returns and Altman Z-scores for configurable portfolios of public companies (e.g., GenAI leaders). It fetches financials and price data from Yahoo Finance, aligns them per filing, and provides robust diagnostics for missing or stale data.

## Features
- Modular, extensible Python codebase
- Configurable portfolios (see `config.py`)
- Per-ticker, per-filing analysis (last 3 financial filings)
- Altman Z-score calculation with robust fallback and missing-field tracking
- YTD and period price change calculation
- Transparent reporting of missing data and staleness
- CLI for portfolio selection and export
- Statistical analysis and plotting of Z-score vs. price change

## Usage

```bash
python evaluate_portfolio.py --portfolio genai --export excel --output my_results.xlsx
```

- `--portfolio`: Portfolio key from config.py (default: genai)
- `--export`: Export to csv or excel
- `--output`: Output filename (optional, default is based on portfolio name)

## Configuration
Edit `config.py` to add or modify portfolios, tickers, and diagnostic assumptions. Example:

```python
PORTFOLIOS = {
    "genai": {
        "name": "GenAI Leaders",
        "description": "Top public companies in generative AI and enabling infrastructure.",
        "tickers": [...],
        "diagnostic_assumptions": {
            "safe_zone_threshold": 2.99,
            "grey_zone_min": 1.81,
            "grey_zone_max": 2.99,
            "distress_zone_max": 1.80,
            "notes": "Altman Z-score thresholds are for public manufacturing companies. Interpret with caution for tech/software."
        },
        "currency": "USD",
        "region": "US"
    }
}
```

## Requirements
- Python 3.8+
- pandas
- yfinance
- openpyxl (for Excel export)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Cleaning and Formatting
To clean the workspace and format code before committing:
```bash
rm -rf __pycache__ *.pyc .ipynb_checkpoints
black *.py
pip freeze > requirements.txt
```

## Output
- Results are printed to the console and can be exported to CSV or Excel.
- Missing or incomplete data is reported as warnings and in the output file.
- Z-score diagnostics are based on configurable thresholds in `config.py`.
- If Z-score or price data is missing for a stock/period, the output will indicate which fields are missing.

## Limitations
- Yahoo Finance may not provide all required financial fields for every stock; missing data is transparently reported.
- For richer coverage, consider supplementing with additional data sources.

## Preparing to Commit
- Ensure all code is formatted and the workspace is clean (see above).
- Review the output and logs for any unexpected warnings or errors.
- Commit all source files, requirements.txt, and the updated README.md.