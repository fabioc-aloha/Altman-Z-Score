# Codebase Flow: Altman Z-Score Analysis Tool

## High-Level Flow Diagram
```
┌──────────────┐
│   main.py    │
└──────┬───────┘
       ↓
┌──────┴──────────────┐     ┌─────────────────┐
│ CLI & Orchestration │ ←── │ .env & settings │
│ (click, logging,    │     └─────────────────┘
│  one_stock_analysis)│
└──────┬──────────────┘
       ↓
┌──────┴──────────────┐     ┌──────────────────────┐
│ Data Fetching       │ ←── │ src/altman_zscore    │
│ (financials,        │     │ /api + data_fetching │
│  prices, executives)│     └──────────────────────┘
└──────┬──────────────┘
       ↓
┌──────┴────────────┐     ┌───────────────────┐
│ Validation        │ ←── │ src/altman_zscore │
│ (Pydantic schemas)│     │ /validation       │
└──────┬────────────┘     └───────────────────┘
       ↓
┌──────┴────────────┐
│ Computation       │
│ (compute_zscore)  │
└──────┬────────────┘
       ↓
┌──────┴────────────┐     ┌───────────────────┐
│ Reporting         │ ─── │ CSV, JSON, PNG,   │
│ (output_generation│     │ terminal display  │
│  + plotting)      │     └───────────────────┘
└───────────────────┘
```

## Detailed Processing Flow
```
main.py
  ↓
Parse CLI args & logging setup (main.py)
  ↓
Invoke analyze_one_stock() in src/altman_zscore/core/one_stock_analysis.py
  ↓
Data Fetching Layer (src/altman_zscore/data_fetching + src/altman_zscore/api):
  ├── fetch_financials (SEC EDGAR primary; yfinance fallback)
  ├── fetch_prices (Yahoo Finance market data)
  └── fetch_executive_data (company officers)
  ↓
Validation Layer (src/altman_zscore/validation/data_validation.py + schemas):
  ├── Pydantic schema checks (src/altman_zscore/schemas)
  └── Report missing/invalid fields
  ↓
Computation Layer (src/altman_zscore/computation):
  ├── compute_zscore.compute_zscore (component calculations)
  └── model_selection logic
  ↓
Reporting & Output Layer:
  ├── output_generation (CSV/JSON metadata)
  ├── plotting_main (trend visualization)
  └── file_operations (write outputs)
  ↓
Terminal Display (src/altman_zscore/core/reporting.py)
```

## Key Supporting Modules

### Core Components
- `main.py`: Entry point, CLI interface and orchestrates analysis.
- `src/altman_zscore/core/one_stock_analysis.py`: Orchestrates the end-to-end stock analysis pipeline.
- `src/altman_zscore/core/data_processing.py`: Data cleaning and transformation utilities.
- `src/altman_zscore/core/file_operations.py`: File I/O helpers for reading/writing JSON, CSV, and metadata.
- `src/altman_zscore/core/output_generation.py`: Generates structured CSV/JSON output.
- `src/altman_zscore/core/reporting.py`: Formats and displays terminal reports.
- `src/altman_zscore/company_profile.py`: Fetches and manages company profile data.

### Data Fetching Layer
- `src/altman_zscore/data_fetching/financials.py`: Fetches and processes financial statements (SEC EDGAR, yfinance fallback).
- `src/altman_zscore/data_fetching/prices.py`: Fetches market price data (Yahoo Finance).
- `src/altman_zscore/data_fetching/executives.py`: Retrieves company executive information.

### API Clients
- `src/altman_zscore/api/sec_client.py`: SEC EDGAR XBRL client.
- `src/altman_zscore/api/yahoo_helpers.py`: Helper functions for Yahoo Finance API.
- `src/altman_zscore/api/openai_client.py`: Azure OpenAI field-mapping and reconciliation.
- `src/altman_zscore/api/finnhub_client.py`: Finnhub market metrics client.

### Computation & Modeling
- `src/altman_zscore/computation/compute_zscore.py`: Implements component-level Z-Score calculations.
- `src/altman_zscore/computation/compute.py`: High-level Z-Score computation orchestration.
- `src/altman_zscore/computation/model_selection.py`: Model selection logic for different Z-Score variants.
- `src/altman_zscore/models`: Data models and enumerations for financial metrics and Z-Score models.

### Validation Layer
- `src/altman_zscore/validation/data_validation.py`: Pydantic schemas and validation logic.
- `src/altman_zscore/schemas`: JSON schema definitions for input/output data.

### Output & Visualization
- `src/altman_zscore/plotting/plot_blocks.py`: Modular plotting utilities for Z-Score and price trend.
- `src/altman_zscore/plotting/plotting_main.py`: Orchestrates figure creation and saving.
- `src/altman_zscore/utils`: Utility helpers (paths, retry, etc.)

## Output Directory Structure
```
output/
  └── TICKER/
      ├── zscore_TICKER.csv               # Z-Score calculations by quarter
      ├── zscore_TICKER.json              # Structured Z-Score data
      ├── zscore_TICKER_metadata.json     # Analysis metadata
      ├── zscore_TICKER_trend.png         # Z-Score trend visualization
      ├── zscore_TICKER_zscore_full_report.md # Full markdown report (trend, commentary)
      ├── reconciliation_result.json      # Data reconciliation results
      ├── company_info.json               # Company profile and metadata
      ├── sec_facts_raw.json              # Raw SEC EDGAR data
      ├── sec_filtered.json               # Filtered/processed SEC data
      ├── yahoo_raw.json                  # Raw Yahoo Finance data
      ├── yahoo_filtered.json             # Filtered/processed Yahoo data
      ├── weekly_prices.csv               # Market price data (CSV)
      ├── weekly_prices.json              # Market price data (JSON)
      ├── yf_info.json                    # Yahoo Finance company info
      ├── TICKER_logo.png                 # Company logo (if available)
      ├── llm_commentary_prompt.txt       # LLM prompt for commentary
      └── reconcile_prompt.txt            # LLM prompt for reconciliation
```

- All files are generated per ticker in a dedicated subfolder (e.g., `output/MSFT/`).
- Some files (e.g., logo, prompts) are optional and may not appear for all tickers.
- File naming is consistent: `zscore_TICKER.*` for Z-Score outputs, `*_raw.json` for raw data, `*_filtered.json` for processed data.
- Both CSV and JSON formats are provided for key outputs where applicable.
- Markdown report and LLM prompt files support explainability and AI-first workflows.

## Recent Features

### Data Integration
- **Multi-source data fetching**: SEC EDGAR, Yahoo Finance, Finnhub
- **Enhanced data validation** with Pydantic schemas
- **Robust error handling** for API failures and data gaps

### Analysis Capabilities
- **Historical trend analysis** with visualization
- **Quarterly Z-Score calculations**
- **Market value integration** for accurate scoring

### Output & Reporting
- **Multiple output formats**: JSON, CSV, PNG
- **Detailed metadata capture**
- **Terminal-friendly display**

### Code Quality
- **Comprehensive test suite** in `/tests`
- **Type hints** throughout codebase
- **Modular architecture** for easy extension

## Testing
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Data Processing Tests**: Validation of calculations
- **API Mock Tests**: External service interaction testing
