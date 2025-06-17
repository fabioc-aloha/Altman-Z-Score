# Altman Z-Score Analysis Pipeline: Codebase Flow (2025)

## Overview
**IMPORTANT**: This tool is strictly limited to U.S.-based companies only. Non-U.S. companies, including ADRs and companies filing Form 20-F, are detected and rejected early in the pipeline.

## High-Level Flow Diagram (with Inputs & Outputs in Boxes)
```
┌──────────────────────────────────────────────────────────────┐
│ Input Validation & U.S. Company Check                        │
│ Inputs: ticker, start_date                                   │
│ Process: Validate ticker, check U.S. status via Yahoo/SEC    │
│ Outputs: company_status.json, NOT_AVAILABLE marker if needed │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ Company Classification & Model Selection                     │
│ Inputs: ticker, company_info.json (optional)                 │
│ Process: Classify industry, SIC, select U.S.-specific model  │
│ Outputs: Model selection, company_info.json                  │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ Data Fetching Layer                                          │
│ Inputs: SEC EDGAR API (financials),                          │
│         Yahoo Finance API (prices/info)                      │
│ Process: Fetch SEC financials, Yahoo prices, company info    │
│ Outputs: sec_facts_raw.json, weekly_prices.csv,              │
│          weekly_prices.json, yf_info.json,                   │
│          yahoo_raw.json, TICKER_logo.png, company_info.json  │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ LLM Field Mapping (SEC)                                      │
│ Inputs: sec_facts_raw.json, canonical field list             │
│ Process: Prompt LLM to map canonical fields to plausible SEC │
│          field names (all plausible candidates, fallback)    │
│ Outputs: field_mapping_prompt_simple.txt,                    │
│          field_mapping_response_simple.json                  │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ Data Reconciliation & Fallback Logic                         │
│ Inputs: sec_facts_raw.json,                                  │
│         field_mapping_response_simple.json                   │
│ Process: For each period and canonical field, try all        │
│          mapped SEC fields in order (robust fallback)        │
│ Outputs: reconciliation_result.json                          │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ Validation (Pydantic schemas)                                │
│ Inputs: reconciliation_result.json                           │
│ Process: Check for missing/invalid fields, log issues        │
│ Outputs: Validated canonical data                            │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ Computation (compute_zscore)                                 │
│ Inputs: validated canonical data                             │
│ Process: Compute Altman Z-Score, model selection logic       │
│ Outputs: zscore_TICKER.csv, zscore_TICKER.json,              │
│          zscore_TICKER_metadata.json                         │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ Reporting & Output Layer                                     │
│ Inputs: zscore_TICKER.json, zscore_TICKER_metadata.json,     │
│         reconciliation_result.json                           │
│ Process: Output generation (CSV/JSON/PNG/Markdown),          │
│          plotting (trend visualization), save all outputs    │
│ Outputs: zscore_TICKER_trend.png,                            │
│          zscore_TICKER_zscore_full_report.md,                │
│          llm_commentary_prompt.txt,                          │
│          all files in output/TICKER/                         │
└──────────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ Terminal Display & Logging                                   │
│ Inputs: All outputs above                                    │
│ Process: Display results, log errors and progress            │
│ Outputs: Terminal output, logs                               │
└──────────────────────────────────────────────────────────────┘
```

## Key Pipeline Details
- **U.S. Company Focus:** Only U.S.-based companies filing standard SEC forms (10-K, 10-Q) are supported. International companies, ADRs, and Form 20-F filers are rejected early.
- **Early Detection:** Non-U.S. companies are detected at pipeline entry using Yahoo Finance metadata (country, exchange, ADR status) and SEC lookup.
- **Historical Data Support:**
  - Default analysis starts from 3 years ago (36 months)
  - Full historical data (often 15+ years) available for most U.S. companies via SEC EDGAR
  - No artificial limits on historical data range
- **Model Types:**
  - Original Z-Score (public manufacturing)
  - Private Company Z'-Score
  - Service Industry Model
  - Financial Industry Model
  - Retail Industry Model
  - ZETA® Credit Risk Model
- **SEC-Only Financials:** All financial data for Z-Score is sourced exclusively from SEC EDGAR. Yahoo is only used for market prices and company info, not for financials or reconciliation.
- **LLM-First Field Mapping:** Canonical fields are mapped to SEC field names using an LLM prompt. The LLM returns all plausible candidates for each canonical field, enabling a robust fallback strategy.
- **Python Fallback Strategy:** For each period and canonical field, the code tries each mapped SEC field in order, using the first available value.
- **Full Traceability:** Both the LLM prompt and response are saved for each run, supporting transparency and debugging.
- **Robust Error Handling:** All steps include error handling and logging. If LLM output is malformed, the error is reported and the pipeline halts for that ticker.
- **Graceful Handling of Missing Data:** If a quarter has no usable financial data, the pipeline skips/report it with a user-friendly message in the output.

## Output Directory Structure
```
output/
  └── TICKER/
      ├── company_status.json                 # Company status and validation results
      ├── NOT_AVAILABLE.txt                   # Present if company is non-U.S. or data unavailable
      ├── zscore_TICKER.csv                   # Z-Score calculations by quarter
      ├── zscore_TICKER.json                  # Structured Z-Score data
      ├── zscore_TICKER_metadata.json         # Analysis metadata & U.S. status
      ├── zscore_TICKER_trend.png             # Z-Score trend visualization
      ├── reconciliation_result.json          # Data reconciliation results
      ├── sec_facts_raw.json                  # Raw SEC EDGAR data
      ├── field_mapping_prompt_simple.txt     # LLM field mapping prompt
      ├── field_mapping_response_simple.json  # LLM field mapping response
      ├── weekly_prices.csv                   # Market price data
      ├── weekly_prices.json                  # Structured price data
      ├── yahoo_raw.json                      # Company metadata
      ├── yf_info.json                        # Additional Yahoo data
      └── TICKER_logo.png                     # Company logo
```

## Date Range Handling
- **Default Range:** Analysis starts from 36 months (3 years) ago by default
- **Historical Data:** Users can request any historical range via --start parameter
- **Data Availability:**
  - SEC EDGAR data typically available from 2009 onwards
  - No artificial limits on historical data
  - Actual range depends on company's SEC filing history
- **Future Protection:** Start dates cannot be in the future

## Implementation & Codebase Notes (2025-06-17)
- All dead code, unused variables, and deprecated files have been removed. The pipeline is now clean and robust.
- The `stock_prices` variable is only assigned and used where required for downstream reporting and plotting.
- All error handling, logging, and fallback logic is up-to-date and matches the codebase.
- The flow diagram and step descriptions above are current and reflect the actual code logic as of this date.
- All outputs, LLM prompts/responses, and reconciliation steps are fully traceable and saved per run.

## Troubleshooting & Analysis
For systematic analysis of pipeline outputs and debugging, see `copilot.md` which provides:
- **Comprehensive Analysis Workflow:** Step-by-step instructions for evaluating ticker analysis completeness
- **VS Code Tool Integration:** Uses available tools (list_dir, read_file, grep_search, run_in_terminal) for systematic analysis
- **Issue Pattern Detection:** Methods for identifying common failure modes and root causes
- **Solution Documentation:** Required audit trail before implementing any code changes

**Key Files for Debugging:**
- `copilot.md` - LLM Copilot analysis instructions
- `Copilot_Troubleshoot.md` - Created during analysis to log findings (audit trail)
- Output files in `output/TICKER/` - Generated pipeline results for analysis

**Common Analysis Commands:**
```bash
# Analyze specific ticker with debug output
python main.py TICKER --start 2024-01-01 --log-level DEBUG

# Test pipeline with multiple tickers
python main.py MSFT AAPL TSLA --start 2024-01-01
```
