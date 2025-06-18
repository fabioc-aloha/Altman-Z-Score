# Altman Z-Score Analysis Pipeline: Codebase Flow (2025)

## Overview
**IMPORTANT**: This tool is strictly limited to U.S.-based companies only. Non-U.S. companies, including ADRs and companies filing Form 20-F, are detected and rejected early in the pipeline.

## High-Level Flow Diagram (10 Steps - Matches Actual Execution)
```
┌──────────────────────────────────────────────────────────────┐
│ 1. Input Validation                                          │
│ Inputs: ticker, start_date                                   │
│ Process: Validate ticker format, check U.S. company status   │
│ Outputs: Validated inputs, early rejection if non-U.S.       │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Fetch Company Profile                                     │
│ Inputs: ticker, comprehensive SEC cache (10,033+ companies)  │
│ Process: CIK lookup, company classification, model selection │
│ Outputs: company_info.json, selected model, profile data     │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Fetch Financials (SEC EDGAR) & Market Data (Yahoo)        │
│ Inputs: CIK, ticker, date range, selected model              │
│ Process: SEC EDGAR → financial facts, Yahoo → market data    │
│ Outputs: sec_facts_raw.json, financials_quarterly.json,      │
│          field_mapping_prompt.txt, recommendations.json,     │
│          major_holders.json, historical_prices.csv           │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Z-Score Computation                                       │
│ Inputs: reconciled financial data, selected model            │
│ Process: Calculate Altman Z-Score for each valid quarter     │
│ Outputs: Z-Score calculations, risk zones, metadata          │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Raw Data Output (CSV/JSON)                                │
│ Inputs: Z-Score results, financial data                      │
│ Process: Format and save structured analysis results         │
│ Outputs: zscore_TICKER.csv, zscore_TICKER.json,              │
│          zscore_TICKER_metadata.json                         │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Fetch Market Data (Prices, Splits, Dividends)             │
│ Inputs: ticker, date range                                   │
│ Process: Download Yahoo Finance data, company info, logo     │
│ Outputs: weekly_prices.csv, weekly_prices.json,              │
│          yahoo_raw.json, yf_info.json, TICKER_logo.png       │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. LLM Prompt Construction                                   │
│ Inputs: Z-Score data, company info, market data              │
│ Process: Build comprehensive analysis prompt with all data   │
│ Outputs: llm_commentary_prompt.txt                           │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 8. LLM Report Generation                                     │
│ Inputs: constructed LLM prompt                               │
│ Process: Generate comprehensive financial analysis report    │
│ Outputs: zscore_TICKER_zscore_full_report.md                 │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 9. Chart Generation                                          │
│ Inputs: Z-Score data, market prices, date range              │
│ Process: Create Z-Score and price trend visualization        │
│ Outputs: zscore_TICKER_trend.png                             │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│ 10. Final File Output                                        │
│ Inputs: All generated files and analysis results             │
│ Process: Organize output directory, display summary          │
│ Outputs: Complete organized output/TICKER/ directory         │
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
- **Model Selection:** Automatic model selection based on company profile (industry, sector, SIC code), with optional force override via `--model` parameter
- **Force Model Override:** Users can force a specific model using `--model` parameter (values: original, private, financial, zeta, retail, emerging)
- **Clean Data Architecture:** 
  - **SEC EDGAR:** Sole source for financial facts (balance sheet, income statement, cash flow)
  - **Yahoo Finance:** Sole source for market data (stock prices, shares outstanding, market cap, analyst recommendations, institutional holdings)
  - **AI Field Mapping:** LLM-powered mapping from SEC GAAP concepts to Z-Score canonical fields
  - **No Data Mixing:** Clean separation eliminates conflicts and ensures data consistency
- **LLM-First Field Mapping:** Canonical fields are mapped to SEC field names using an LLM prompt. The LLM returns all plausible candidates for each canonical field, enabling a robust fallback strategy.
- **Python Fallback Strategy:** For each period and canonical field, the code tries each mapped SEC field in order, using the first available value.
- **Full Traceability:** Both the LLM prompt and response are saved for each run, supporting transparency and debugging.
- **Robust Error Handling:** All steps include error handling and logging. If LLM output is malformed, the error is reported and the pipeline halts for that ticker.
- **Graceful Handling of Missing Data:** If a quarter has no usable financial data, the pipeline skips/report it with a user-friendly message in the output.

## CIK Cache System (New as of 2025-06-17)
The system now includes a **CIK cache** that dramatically improves reliability and performance:

- **User Cache:** Downloadable/updatable cache at `src/altman_zscore/api/cache/sec_company_tickers_cache.json` containing 10,000+ U.S. companies
- **Automatic Updates:** System tries to refresh cache weekly; downloads fresh data from SEC API if cache is missing or expired
- **No More Rate Limits:** Eliminates SEC API 403/429 errors for virtually all U.S. public companies
- **Instant Lookups:** CIK resolution for AAPL, MSFT, TSLA, etc. happens immediately without API calls

**Cache Commands:**
```bash
# Update cache manually (downloads latest SEC database)
python main.py --update-cache

# Regular analysis uses cached data automatically  
python main.py TICKER --date 2024-01-01
```

## Output Directory Structure
```
output/
  └── TICKER/
      ├── company_status.json                 # Company status and validation results
      ├── TICKER_NOT_AVAILABLE.txt            # Present if company is non-U.S. or data unavailable
      ├── zscore_TICKER.csv                   # Z-Score calculations by quarter
      ├── zscore_TICKER.json                  # Structured Z-Score data
      ├── zscore_TICKER_metadata.json         # Analysis metadata & U.S. status
      ├── zscore_TICKER_trend.png             # Z-Score trend visualization
      ├── zscore_TICKER_zscore_full_report.md # Comprehensive LLM analysis report
      ├── reconciliation_result.json          # Data reconciliation results
      ├── sec_facts_raw.json                  # Raw SEC EDGAR data
      ├── field_mapping_prompt.txt            # LLM field mapping prompt (ticker-specific)
      ├── field_mapping_response_simple.json  # LLM field mapping response
      ├── llm_commentary_prompt.txt           # LLM report generation prompt
      ├── weekly_prices.csv                   # Market price data
      ├── weekly_prices.json                  # Structured price data
      ├── yahoo_raw.json                      # Company metadata
      ├── yf_info.json                        # Additional Yahoo data
      └── TICKER_logo.png                     # Company logo
```

## Date Range Handling
- **Default Range:** Analysis starts from 36 months (3 years) ago by default
- **Historical Data:** Users can request any historical range via --date parameter
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
python main.py TICKER --date 2024-01-01 --log-level DEBUG

# Force specific model for analysis
python main.py TICKER --model financial --date 2024-01-01

# Test pipeline with multiple tickers
python main.py MSFT AAPL TSLA --date 2024-01-01

# Update SEC cache and analyze
python main.py --update-cache
python main.py TICKER --date 2024-01-01
```

## Recent Improvements (2025-06-17)
- **✅ Comprehensive SEC Cache:** Pre-shipped database with 10,033+ companies eliminates API rate limiting
- **✅ Improved File Organization:** Field mapping prompts now saved to ticker-specific folders
- **✅ Enhanced Model Selection:** Robust validation and fallback mechanisms
- **✅ Cache Auto-Management:** Weekly auto-refresh with graceful fallbacks to shipped cache
- **✅ Progress Tracking:** Accurate 10-step progress bar matching actual pipeline execution
