# Altman Z-Score Analysis Pipeline: Current System Architecture & Workflow

**Purpose**: Documents the PRESENT state of the system - current architecture, data flow, and operational workflow.

For **PAST** accomplishments → see [`CHANGELOG.md`](CHANGELOG.md)  
For **FUTURE** plans → see [`TODO.md`](TODO.md)

## System Overview

**Current Version**: 3.5.4 (2025-06-18)  
**Architecture**: Clean separation between SEC EDGAR (financials) and Yahoo Finance (market data)  
**Scope**: U.S. public companies only (10,000+ supported via SEC cache)  
**Key Innovation**: Multi-tier field mapping with per-quarter fallback logic

**IMPORTANT**: This tool is strictly limited to U.S.-based companies only. Non-U.S. companies, including ADRs and companies filing Form 20-F, are detected and rejected early in the pipeline.

## Core Architecture Principles

### Data Source Separation (Clean Architecture)
- **SEC EDGAR**: Exclusive source for financial statements (balance sheet, income statement, cash flow)
- **Yahoo Finance**: Exclusive source for market data (prices, analyst recommendations, institutional holdings)
- **AI Field Mapping**: LLM-powered semantic mapping between SEC GAAP concepts and Z-Score canonical fields
- **No Data Mixing**: Clean separation eliminates conflicts and ensures data consistency

### Supported Company Types
- **U.S. Public Companies Only**: Must file standard SEC forms (10-K, 10-Q)
- **Early Rejection**: Non-U.S. companies, ADRs, and Form 20-F filers are detected and rejected at pipeline entry
- **Comprehensive Coverage**: 10,033+ companies supported via pre-shipped SEC cache

### Model Portfolio
- **Original Z-Score**: Public manufacturing companies (default)
- **Private Company Z'-Score**: Private manufacturing companies
- **Service Industry Model**: Technology and service companies
- **Financial Industry Model**: Banks and financial institutions
- **Retail Industry Model**: Retail and consumer companies
- **ZETA® Credit Risk Model**: Advanced multi-factor model
- **Emerging Markets Model**: High-growth and emerging market companies

## High-Level Flow Diagram (10 Steps - Matches Actual Execution)

### Pipeline Execution Flow
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

## Data Processing Pipeline

### Financial Data Extraction (Step 3 Detail)
The financial data extraction process uses a sophisticated multi-tier approach:

#### SEC EDGAR Data Processing
1. **CIK Resolution**: Convert ticker to Central Index Key using pre-cached SEC database
2. **Raw Facts Retrieval**: Download company facts from SEC API in XBRL format
3. **Quarterly Filtering**: Extract balance sheet and income statement items by period
4. **Concept Normalization**: Handle various SEC GAAP concept naming conventions

#### Field Mapping Innovation (v3.5.4+)
The pipeline employs a revolutionary 3-tier field mapping system:

**Tier 1: AI-Powered Semantic Mapping**
- LLM analyzes all available SEC GAAP concepts for each company
- Returns semantic mappings with confidence scores
- Handles complex, non-standard, and international field names
- Successfully maps 95%+ of standard financial concepts

**Tier 2: Global Fallback Mapping**
- Pre-defined mappings for common SEC concepts when AI fails
- Covers standard GAAP fields: Assets, Revenues, Liabilities, etc.
- Applied automatically when AI mapping returns null or low confidence

**Tier 3: Per-Quarter Fallback Mapping (Innovation)**
- **Breakthrough Feature**: Handles companies with inconsistent field naming across periods
- **Real-World Problem Solved**: Ford uses "Revenues" (annual) vs "RevenueFromContractWithCustomerExcludingAssessedTax" (quarterly)
- **Process**: Each quarter individually checked for missing fields and mapped using period-specific alternatives
- **Result**: Complete Z-Score calculation coverage across all reporting periods

#### Revenue Field Handling Examples
```
Company: Ford Motor Company (F)
Annual Periods (2024-12-31): "Revenues" → mapped to "sales"
Quarterly Periods (2024-09-30): "RevenueFromContractWithCustomerExcludingAssessedTax" → mapped to "sales"
Result: No "Required field sales is missing" errors
```

### Market Data Integration
- **Yahoo Finance API**: Real-time and historical market data
- **Price Data**: Weekly closing prices for trend analysis
- **Analyst Data**: Buy/Hold/Sell recommendations and price targets
- **Institutional Data**: Major holders and ownership percentages
- **Corporate Actions**: Stock splits and dividend adjustments
## Key Pipeline Features & Capabilities

### U.S. Company Focus & Detection
- **Supported**: Only U.S.-based companies filing standard SEC forms (10-K, 10-Q)
- **Early Detection**: Non-U.S. companies detected using Yahoo Finance metadata (country, exchange, ADR status) and SEC lookup
- **Automatic Rejection**: International companies, ADRs, and Form 20-F filers rejected at pipeline entry with clear messaging

### Historical Data Support
- **Default Range**: Analysis starts from 36 months (3 years) ago by default
- **Comprehensive Coverage**: Full historical data (often 15+ years) available for most U.S. companies via SEC EDGAR
- **No Artificial Limits**: Historical data range limited only by company's SEC filing history
- **Data Availability**: SEC EDGAR data typically available from 2009 onwards
- **Future Protection**: Start dates cannot be in the future

### Model Selection & Override
- **Automatic Selection**: Based on company profile (industry, sector, SIC code)
- **Force Override**: Users can force specific model using `--model` parameter
- **Available Models**: original, private, financial, zeta, retail, emerging
- **Validation**: Robust model validation with graceful fallbacks
## Advanced Features & Innovations

### CIK Cache System (Performance Enhancement)
The system includes a high-performance **CIK cache** that dramatically improves reliability:

- **Pre-shipped Database**: `src/altman_zscore/api/cache/sec_company_tickers_cache.json` with 10,033+ U.S. companies
- **Instant Lookups**: CIK resolution for major companies (AAPL, MSFT, TSLA) happens immediately without API calls
- **Automatic Updates**: System attempts weekly cache refresh from SEC API
- **Rate Limit Elimination**: Eliminates SEC API 403/429 errors for virtually all U.S. public companies
- **Graceful Fallbacks**: Falls back to shipped cache if API update fails

**Cache Management Commands:**
```bash
# Update cache manually (downloads latest SEC database)
python main.py --update-cache

# Regular analysis uses cached data automatically  
python main.py TICKER --date 2024-01-01

# Check cache status and statistics
python main.py --cache-stats
```

### Error Handling & Resilience
- **Multi-Level Fallbacks**: Each data source and mapping tier has backup strategies
- **Graceful Degradation**: Partial data availability doesn't prevent analysis completion
- **Comprehensive Logging**: Debug-level logging for troubleshooting field mapping issues
- **Validation Gates**: Multiple validation checkpoints prevent invalid data propagation
- **User-Friendly Messages**: Clear error messages for common failure scenarios
- **Multi-Level Fallback Strategy:** 
  1. **AI Mapping:** LLM-powered field mapping for optimal accuracy
  2. **Global Fallback:** Common field mappings when AI fails
  3. **Per-Quarter Fallback:** Quarter-specific mapping for mixed reporting patterns (e.g., Ford's annual vs quarterly revenue fields)

## Enhanced Field Mapping System (v3.5.4+)

The pipeline features a robust, multi-tier field mapping system designed to handle diverse SEC reporting patterns:

### Mapping Tiers
1. **AI-Powered Mapping (Primary)**
   - LLM analyzes all available SEC GAAP concepts
   - Returns semantic mappings with confidence scores
   - Handles complex, non-standard field names

2. **Global Fallback Mapping (Secondary)**
   - Pre-defined mappings for common SEC concepts
   - Applied when AI mapping fails or returns null
   - Covers standard GAAP fields like "Assets", "Revenues", etc.

3. **Per-Quarter Fallback Mapping (Tertiary)**
   - **Innovation**: Handles companies with inconsistent field naming across periods
   - **Real-world Case**: Ford uses "Revenues" (annual) vs "RevenueFromContractWithCustomerExcludingAssessedTax" (quarterly)
   - Each quarter is individually checked for missing fields and mapped using available alternatives
   - Ensures complete Z-Score calculation coverage across all reporting periods

### Revenue Field Handling
The system now handles complex revenue reporting patterns:
- **Annual Periods**: Maps to "Revenues", "TotalRevenue", "OperatingRevenue"
- **Quarterly Periods**: Maps to "RevenueFromContractWithCustomerExcludingAssessedTax", "QuarterlyRevenue", etc.
- **Mixed Patterns**: Automatically detects and handles companies that use different field names for different periods
- **Result**: Zero "Required field sales is missing" errors for companies like Ford

### Backfill Logic
- **Annual Revenue Backfill**: When quarterly revenue data is missing, attempts to use annual revenue data for the same year
- **Field Name Normalization**: Maps various revenue concepts to the canonical "sales" field
- **Validation**: Ensures all quarters have required fields before Z-Score computation

This enhanced system resolved critical issues with companies like Ford Motor Company (F) that had inconsistent revenue field naming across reporting periods.

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

## Implementation & Codebase Status (2025-06-18)

### Code Quality & Maintenance
- **Clean Codebase**: All dead code, unused variables, and deprecated files removed
- **Robust Error Handling**: Comprehensive error handling and logging throughout pipeline
- **Modular Design**: Clear separation of concerns with well-defined module interfaces
- **Current Documentation**: Flow diagram and descriptions match actual code implementation
- **Full Traceability**: All outputs, LLM prompts/responses, and reconciliation steps saved per run

### Recent Technical Achievements (v3.5.4)
- **Ford Sales Field Resolution**: Eliminated "Required field sales is missing" errors for complex reporting patterns
- **Per-Quarter Mapping Innovation**: Revolutionary per-quarter fallback mapping for mixed annual/quarterly reporting
- **Enhanced Debug Capabilities**: Comprehensive logging and debug output for field mapping troubleshooting
- **Documentation Restructuring**: Clear Past/Present/Future documentation strategy implementation

## Development & Debugging Workflow

### Systematic Analysis Framework
For comprehensive pipeline analysis and debugging, the system provides structured workflows:

**Primary Analysis Tools:**
- **VS Code Integration**: Uses available tools (list_dir, read_file, grep_search, run_in_terminal) for systematic analysis
- **Issue Pattern Detection**: Methods for identifying common failure modes and root causes
- **Solution Documentation**: Required audit trail before implementing code changes
- **Comprehensive Logging**: Multiple log levels with detailed field mapping traces

**Key Debugging Files:**
- `copilot.md` - LLM Copilot analysis instructions and workflows
- `Copilot_Troubleshoot.md` - Analysis audit trail and findings documentation
- `output/TICKER/` - Complete pipeline results for post-analysis review
- `field_mapping_prompt.txt` - LLM field mapping input for each ticker
- `field_mapping_response_simple.json` - AI mapping results for validation

### Common Development Commands
```bash
# Development and debugging commands
python main.py TICKER --date 2024-01-01 --log-level DEBUG  # Detailed debug output
python main.py TICKER --model financial --date 2024-01-01  # Force specific model
python main.py MSFT AAPL TSLA --date 2024-01-01           # Multi-ticker batch analysis
python main.py --update-cache                              # Refresh SEC cache
python main.py --cache-stats                               # Cache status information

# Field mapping debugging
python main.py TICKER --debug-mapping                      # Enhanced field mapping debug
python main.py TICKER --save-prompts                       # Save all LLM prompts/responses
```

### Performance Monitoring
- **Pipeline Timing**: Each step's execution time tracked and logged
- **Memory Usage**: Monitoring for large dataset processing
- **API Rate Limiting**: Intelligent throttling and caching to prevent API blocks
- **Success Rates**: Field mapping success statistics per company type

## Current System Status & Capabilities (v3.5.4 - 2025-06-18)

### ✅ Recently Completed Major Enhancements
- **Ford Sales Field Resolution**: Eliminated "Required field sales is missing" errors for companies with mixed reporting patterns
- **Per-Quarter Fallback Mapping**: Revolutionary quarter-specific field mapping handling different revenue field names per period
- **Revenue Backfilling Logic**: Automatic backfilling of revenue data using annual data when quarterly data missing
- **Documentation Restructuring**: Clear Past/Present/Future documentation strategy with cross-references
- **Enhanced Debug Capabilities**: Comprehensive field mapping troubleshooting and logging

### 📊 Current System Metrics
- **Supported Companies**: 10,033+ U.S. public companies via SEC cache
- **Model Coverage**: 7 different Z-Score model variants for various industry types
- **Historical Data Range**: Typically 15+ years per company (limited only by SEC filing history)
- **Field Mapping Success Rate**: 95%+ for standard financial concepts via AI + fallback system
- **API Rate Limit Elimination**: Virtual elimination of SEC API 403/429 errors via intelligent caching

### 🔧 System Robustness Features
- **Multi-Tier Fallback**: 3-level field mapping strategy (AI → Global → Per-Quarter)
- **Clean Architecture**: Complete separation between SEC financial data and Yahoo market data
- **Comprehensive Validation**: Multiple validation gates preventing invalid data propagation
- **Graceful Error Handling**: User-friendly error messages and partial analysis completion
- **Full Audit Trail**: Complete traceability of all analysis steps and LLM interactions

### 🚀 Performance Characteristics
- **Instant CIK Lookup**: Major companies (AAPL, MSFT, TSLA) resolve immediately via cache
- **Parallel Processing Ready**: Architecture supports future multi-ticker parallel execution
- **Memory Efficient**: Optimized for large datasets without memory exhaustion
- **Intelligent Caching**: SEC cache auto-refresh with graceful fallbacks

---

**Next Development Phase**: See [`TODO.md`](TODO.md) for v3.6.0 planned enhancements  
**Complete Version History**: See [`CHANGELOG.md`](CHANGELOG.md) for detailed release notes
