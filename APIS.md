# Vision Alignment

All API and data source decisions are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

## Strategic Architecture Decision: API-First with FMP

**KEY INSIGHT**: The refactored architecture eliminates the need for complex SEC EDGAR field mapping by leveraging Financial Modeling Prep (FMP) as the primary source for **pre-calculated financial metrics**.

**Strategic Benefits:**
1. **FMP provides all Z-Score ratios pre-calculated** (Working Capital/Total Assets, EBIT/Total Assets, etc.)
2. **Eliminates field mapping complexity** - no need to parse/map SEC XBRL concepts
3. **Deterministic data pipeline** - consistent metric definitions across all companies
4. **48-hour caching** - optimal balance of data freshness and API efficiency
5. **Clear data source separation** - FMP for financials, Yahoo for market data

**Architecture Impact:**
- SEC EDGAR field mapping/caching is **no longer required** for Z-Score calculations
- FMP provides standardized financial statement data that can be accessed directly
- Data pipeline focuses on integration, quality gates, and caching
- LLM usage limited to commentary and insights generation only

# APIs Documentation

**Purpose**: Documents current API integrations, data sources, and external service configurations.

**Version**: 3.5.5 (2025-06-18) - Updated for current system architecture

For **PAST** API changes → see [`CHANGELOG.md`](CHANGELOG.md)  
For **FUTURE** API plans → see [`TODO.md`](TODO.md)  
For **PRESENT** system architecture → see [`FLOW.md`](FLOW.md)

This document provides details about the external APIs used in the Altman Z-Score project.

## Financial Modeling Prep (FMP) API

### Overview
FMP is the **primary data source** for all financial metrics required for Z-Score calculations. FMP provides standardized financial statement data, eliminating the need for complex field mapping from SEC EDGAR raw data.

### API Configuration
- **Base URL**: `https://financialmodelingprep.com/api/v3`
- **Authentication**: API key required
- **Environment Variable**: `FINANCIAL_MODELING_PREP_API_KEY`
- **Rate Limits**: 250 requests/minute (free tier), configurable
- **Cache TTL**: 48 hours for all financial data

### Key Endpoints for Z-Score Calculation

#### 1. Financial Ratios (`/ratios/{symbol}`)
**PRIMARY ENDPOINT** - Provides all Z-Score ratios pre-calculated:

**Available Z-Score Metrics:**
- **Working Capital Ratio**: `workingCapital / totalAssets` (X₁)
- **Retained Earnings Ratio**: `retainedEarnings / totalAssets` (X₂) 
- **EBIT Ratio**: `ebit / totalAssets` (X₃)
- **Asset Turnover**: `revenue / totalAssets` (X₅)
- **Current Ratio**: For working capital calculations
- **Debt Ratios**: For leverage analysis

**Example Request:**
```bash
curl "https://financialmodelingprep.com/api/v3/ratios/AAPL?period=annual&limit=5&apikey={API_KEY}"
```

#### 2. Income Statement (`/income-statement/{symbol}`)
**Backup data source** for EBIT, Revenue validation:
- `ebit`: Earnings Before Interest and Taxes
- `revenue`: Total Revenue/Sales
- `netIncome`: Net Income

#### 3. Balance Sheet (`/balance-sheet-statement/{symbol}`)  
**Backup data source** for asset/liability validation:
- `totalAssets`: Total Assets
- `totalLiabilities`: Total Liabilities
- `retainedEarnings`: Retained Earnings
- `workingCapital`: Current Assets - Current Liabilities

#### 4. Company Profile (`/profile/{symbol}`)
**Company metadata** for validation and context:
- `companyName`: Official company name
- `sector`: Business sector
- `industry`: Specific industry
- `marketCap`: Market capitalization

### Integration Architecture

**Layer 1: FMP Data Fetch** (`altman_zscore/layers/data_fetch/fmp_fetcher.py`)
- Handles all FMP API calls with caching
- 48-hour TTL for financial data
- Rate limiting integration
- Error handling and retries

**Layer 1: Data Merger** (`altman_zscore/layers/data_fetch/data_merger.py`)
- Combines FMP financial data with Yahoo market data
- Quality gates and validation
- Canonical data model creation

**Strategic Advantage:**
FMP's pre-calculated ratios eliminate the need for:
- SEC EDGAR field mapping complexity
- XBRL concept resolution  
- Custom ratio calculations
- Field name variations across companies

This results in a **deterministic, reliable data pipeline** focused on integration rather than transformation.

## SEC EDGAR APIs

### Company Submissions API
- **Base URL**: `https://data.sec.gov/submissions`
- **Endpoint**: `/CIK{cik}.json` (where CIK is 10-digit with leading zeros)
- **Description**: Provides company filing metadata and general information
- **Authentication**: 
  - Requires User-Agent header in format: `Company/Project Contact-Email`
  - Environment Variable: `SEC_EDGAR_USER_AGENT` or `SEC_USER_AGENT`
  - Example: `AltmanZScore/1.0 name@domain.com`
- **Rate Limits**: 
  - 100ms minimum between requests (0.1 seconds)
  - No authentication or API keys required
  - Must respect HTTP 429 responses
  - Implement exponential backoff for retries
- **Update Schedule**:
  - Real-time updates (< 1 second delay)
  - Data refreshed as filings are disseminated
  - Bulk data updated nightly at 3:00 AM ET
- **Key Fields**:
  - `sic`: Standard Industrial Classification code
  - `sicDescription`: Industry description
  - `flags.foreignPrivateIssuer`: Boolean indicating foreign/ADR status
  - `name`: Company name
  - `tickers`: Array of ticker symbols
- **Example Request**:
```bash
curl -H "User-Agent: AltmanZScore/1.0 name@domain.com" \
     -H "Accept: application/json" \
     https://data.sec.gov/submissions/CIK0000789019.json
```

### Company Facts API (Primary Financial Data Source)
- **Endpoint**: `/CIK{cik}.json` 
- **Description**: **PRIMARY DATA SOURCE** - Provides comprehensive XBRL financial facts for Z-Score calculations
- **Usage**: Core financial data extraction for balance sheet, income statement, and cash flow items
- **Enhanced Processing (v3.5.4+)**:
  - **Multi-Tier Field Mapping**: AI-powered semantic mapping with fallback strategies
  - **Per-Quarter Logic**: Handles companies with different field names across periods (e.g., Ford's annual vs quarterly revenue fields)
  - **Revenue Backfilling**: Automatic use of annual data when quarterly data missing
- **Authentication**: Same as Company Submissions API
- **Rate Limits**: Same as Company Submissions API
- **Example Request**:
```bash
curl -H "User-Agent: AltmanZScore/3.5.5 name@domain.com" \
     -H "Accept: application/json" \
     https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json
```

### CIK Cache System (Performance Enhancement)
- **Local Cache**: Pre-shipped database at `src/altman_zscore/api/cache/sec_company_tickers_cache.json`
- **Coverage**: 10,033+ U.S. public companies
- **Benefits**: 
  - Instant CIK resolution for major companies (AAPL, MSFT, TSLA, etc.)
  - Eliminates SEC API 403/429 rate limit errors
  - Weekly auto-refresh with graceful fallbacks
- **Management Commands**:
```bash
python main.py --update-cache    # Manual cache refresh
python main.py --cache-stats     # Cache status information
```
  - Single Concept: `/CIK{cik}/us-gaap/{concept}.json`
  - All Company Facts: `/CIK{cik}.json`
  - Frame Data: `/us-gaap/{concept}/USD/{period}.json`
- **Description**: Provides normalized XBRL financial data from forms 10-Q, 10-K, 8-K, 20-F, 40-F, 6-K
- **Authentication**: Same as submissions API
- **Rate Limits**: Same as submissions API
- **Update Schedule**: Real-time updates (< 1 minute delay)
- **Core Financial Tags**:
  - Current Assets: `us-gaap:AssetsCurrent`, `us-gaap:CurrentAssets`, `us-gaap:AssetsNetCurrent`
  - Total Assets: `us-gaap:Assets`, `us-gaap:TotalAssets`, `us-gaap:AssetsNet`
  - Retained Earnings: `us-gaap:RetainedEarnings`, `us-gaap:RetainedEarningsAccumulatedDeficit`
  - Operating Income: `us-gaap:OperatingIncomeLoss`, `us-gaap:IncomeLossFromOperations`
  - Total Liabilities: `us-gaap:Liabilities`, `us-gaap:TotalLiabilities`, `us-gaap:LiabilitiesTotal`
  - Revenue: `us-gaap:Revenues`, `us-gaap:RevenueFromContractWithCustomer`, `us-gaap:SalesRevenueNet`
- **Industry-Specific Tags**:
  - Tech/AI:
    * R&D: `us-gaap:ResearchAndDevelopmentExpense`, `us-gaap:TechnologyAndDevelopmentExpense`
    * Subscription Revenue: `us-gaap:SubscriptionRevenue`, `us-gaap:CloudServicesRevenue`
  - Manufacturing:
    * Inventory: `us-gaap:InventoryNet`, `us-gaap:Inventories`
    * COGS: `us-gaap:CostOfGoodsAndServicesSold`, `us-gaap:CostOfRevenue`
    * CapEx: `us-gaap:PaymentsToAcquirePropertyPlantAndEquipment`

### Company Search API 
- **Base URL**: `https://www.sec.gov/cgi-bin/browse-edgar`
- **Description**: Search for companies and filings
- **Parameters**:
  - `CIK`: Company CIK number
  - `type`: Filing type (e.g., "10-Q", "10-K")
  - `dateb`: End date for search
  - `owner`: "include" for ownership filings
- **Authentication**: Same as above
- **Additional Features**:
  - CORS: Not supported on data.sec.gov
  - Bulk Data: Available via nightly ZIP files
    * Companies: `/Archives/edgar/daily-index/xbrl/companyfacts.zip`
    * Submissions: `/Archives/edgar/daily-index/bulkdata/submissions.zip`
- **Example**:
```bash
curl -H "User-Agent: AltmanZScore/1.0 name@domain.com" \
     "https://www.sec.gov/cgi-bin/browse-edgar?CIK=789019&type=10-Q"
```

## Yahoo Finance API

**Note**: This is an unofficial API without formal documentation. Use with caution and implement proper rate limiting and error handling.

### Market Data API
- **Base URL**: `https://query2.finance.yahoo.com/v8/finance`
- **Description**: Provides real-time and historical market data
- **Key Endpoints**:
  - `/chart/{symbol}`: Historical price data
  - `/quote/{symbol}`: Current quote data
- **Parameters**:
  - `interval`: Data interval (1d, 1wk, 1mo)
  - `range`: Historical range (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max)
- **Best Practices**:
  - Implement rate limiting (recommended: 2000ms between requests)
  - Use exponential backoff for retries
  - Cache responses where possible
  - Handle HTTP 429 (Too Many Requests) gracefully
- **Authentication**: Optional API key for premium access
- **Example**:
```bash
curl "https://query2.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=3mo"
```

### Company Information API
- **Base URL**: `https://query1.finance.yahoo.com/v10/finance`
- **Description**: Provides company details and financial metrics
- **Key Endpoints**:
  - `/quoteSummary/{symbol}`: Company profile and metrics
- **Modules** (combine multiple with comma-separation):
  - `assetProfile`: Company information and description
  - `financialData`: Current financial metrics and ratios
  - `defaultKeyStatistics`: Key statistics and indicators
  - `balanceSheetHistory`: Historical balance sheets
  - `incomeStatementHistory`: Historical income statements
  - `cashflowStatementHistory`: Historical cash flow statements
- **Error Handling**:
  - Handle HTTP 401 (Unauthorized)
  - Handle HTTP 404 (Symbol not found)
  - Handle HTTP 429 (Rate limit exceeded)
  - Handle HTTP 500/503 (Server errors)
- **Example**:
```bash
curl "https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=assetProfile,financialData"
```

## Finnhub API

### Overview
- **Base URL**: `https://finnhub.io/api/v1`
- **Description**: Provides company profiles, logos, and additional financial/market data. Used for company profile enrichment and logo fetching in this project.
- **Authentication**: 
  - Requires API key via `FINNHUB_API_KEY` environment variable
  - Free and paid tiers available (see [finnhub.io/docs/api](https://finnhub.io/docs/api))
- **Key Endpoints Used**:
  - `/stock/profile2?symbol={symbol}`: Company profile and logo URL
  - `/stock/metric?symbol={symbol}&metric=all`: Company financial metrics
  - Direct logo URL: `https://static2.finnhub.io/file/publicdatany/finnhubimage/stock_logo/{symbol}.png`
- **Rate Limits**: 
  - Free tier: 60 API calls/minute (see [pricing](https://finnhub.io/pricing))
  - Exceeding limits returns HTTP 429
- **Example Request**:
```bash
curl -H "X-Finnhub-Token: $FINNHUB_API_KEY" \
     "https://finnhub.io/api/v1/stock/profile2?symbol=AAPL"
```

- **References**:
  - [Finnhub API Docs](https://finnhub.io/docs/api)
  - [finnhub-python SDK](https://github.com/Finnhub-Stock-API/finnhub-python)

## Azure OpenAI API (AI-Powered Features)

### Overview
- **Purpose**: AI-powered insights generation and comprehensive financial report analysis
- **Authentication**: Requires `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` environment variables
- **Model**: GPT-4 or equivalent for optimal financial analysis capabilities

### Analysis & Insights API Usage
- **Function**: `generate_financial_insights()` - Analyzes Z-Score results and provides contextual commentary
- **Features**: 
  1. **Risk Assessment**: AI interprets Z-Score values and financial trends
  2. **Industry Context**: Provides sector-specific analysis and benchmarking
  3. **Action Items**: Generates actionable recommendations based on financial health
- **Integration**: All AI interactions logged to `output/{ticker}/llm_interactions/` for auditability

### Report Generation API Usage
- **Function**: `get_llm_qualitative_commentary()` - Generates comprehensive 11-section financial analysis
- **Capabilities**:
  - Executive summaries and diagnostic evaluations
  - Turnaround theory applications and stakeholder recommendations
  - Market sentiment analysis and strategic insights
  - Risk assessments and peer comparisons

### Rate Limiting & Error Handling
- **Intelligent Retry**: Exponential backoff for API failures
- **Comprehensive Logging**: Debug-level logging for troubleshooting
- **Graceful Degradation**: Analysis continues with fallback mappings if AI fails

## Financial Modeling Prep (FMP) API

**Status**: ✅ **PRIMARY DATA SOURCE** for financial statements and Z-Score calculations

### Overview
- **Base URL**: `https://financialmodelingprep.com/api/v3`
- **Description**: Professional-grade financial data API providing normalized financial statements for 10,000+ public companies
- **Authentication**: 
  - Requires API key via `FMP_API_KEY` environment variable
  - Multiple subscription tiers available (see [FMP Pricing](https://financialmodelingprep.com/developer/docs/pricing))
- **Project Usage**: Primary source for income statements, balance sheets, cash flow statements, and financial ratios
- **Data Quality**: ✅ **100% coverage confirmed** for Z-Score and F-Score calculations across multiple sectors

### Core Financial Statement Endpoints

#### Income Statement
- **Endpoint**: `/income-statement/{symbol}`
- **Parameters**:
  - `limit`: Number of periods to return (default: 10, max: 100)
  - `period`: `annual` (default) or `quarter`
  - `apikey`: Your FMP API key
- **Key Fields for Z-Score**:
  - `revenue` / `totalRevenue`: Net sales/revenue
  - `netIncome`: Net income after taxes
  - `grossProfit`: Gross profit (revenue - COGS)
  - `ebit`: Earnings before interest and taxes  
  - `interestExpense`: Interest expense
- **Example**:
```bash
curl "https://financialmodelingprep.com/api/v3/income-statement/AAPL?limit=5&apikey=YOUR_KEY"
```

#### Balance Sheet
- **Endpoint**: `/balance-sheet-statement/{symbol}`
- **Parameters**: Same as income statement
- **Key Fields for Z-Score**:
  - `totalAssets`: Total assets
  - `currentAssets`: Current assets
  - `currentLiabilities`: Current liabilities
  - `totalLiabilities`: Total liabilities
  - `totalStockholdersEquity`: Total shareholders' equity
  - `retainedEarnings`: Retained earnings
  - `longTermDebt`: Long-term debt
- **Example**:
```bash
curl "https://financialmodelingprep.com/api/v3/balance-sheet-statement/AAPL?limit=5&apikey=YOUR_KEY"
```

#### Cash Flow Statement
- **Endpoint**: `/cash-flow-statement/{symbol}`
- **Parameters**: Same as income statement
- **Key Fields for Z-Score**:
  - `operatingCashFlow`: Cash flow from operating activities
  - `netCashProvidedByOperatingActivities`: Alternative operating cash flow field
  - `freeCashFlow`: Free cash flow
  - `capitalExpenditure`: Capital expenditures
- **Example**:
```bash
curl "https://financialmodelingprep.com/api/v3/cash-flow-statement/AAPL?limit=5&apikey=YOUR_KEY"
```

#### Financial Ratios (Optional Enhancement)
- **Endpoint**: `/ratios/{symbol}`
- **Parameters**: Same as income statement
- **Key Fields Available**:
  - `currentRatio`: Current ratio
  - `debtRatio`: Debt ratio
  - `returnOnAssets`: Return on assets
  - `assetTurnover`: Asset turnover ratio
- **Usage**: Pre-computed ratios for validation and cross-checking
- **Example**:
```bash
curl "https://financialmodelingprep.com/api/v3/ratios/AAPL?limit=5&apikey=YOUR_KEY"
```

### Rate Limits and Best Practices
- **Free Tier**: 250 API calls/day
- **Paid Tiers**: 1,000+ calls/day depending on plan
- **Rate Limiting**: Implement 0.5-1 second delays between requests
- **Error Handling**: 
  - HTTP 429: Rate limit exceeded (implement exponential backoff)
  - HTTP 401: Invalid API key
  - HTTP 404: Symbol not found
- **Caching Strategy**: Cache financial data for 24 hours minimum (financial statements change infrequently)

### Data Quality and Coverage
- **Multi-Sector Support**: ✅ Technology, consumer, financial services validated
- **International Support**: ✅ US companies and international ADRs (BBD, ITUB validated)
- **Multi-Currency**: ✅ Data returned in company's reporting currency
- **Historical Depth**: ✅ 5+ years of annual data available
- **F-Score Validation**: ✅ All 9 Piotroski F-Score components calculable
- **Z-Score Support**: ✅ All required fields available for Altman Z-Score models

### Integration with Project Architecture
```python
# Example usage in cache layer
from altman_zscore.cache import store_financial_data, load_financial_data

# Store FMP data  
financial_data = {
    'income_statement': income_data,
    'balance_sheet': balance_data,
    'cash_flow': cashflow_data,
    'ratios': ratios_data
}
store_financial_data('AAPL', financial_data)

# Load cached data
cached_data = load_financial_data('AAPL')
```

### Advantages Over SEC EDGAR Approach
1. **Normalized Data**: No field mapping complexity
2. **Professional Quality**: Data cleaned and standardized
3. **Faster Implementation**: Direct access to financial metrics
4. **Multi-Currency**: Proper handling of international companies
5. **Rate Limiting**: More predictable API behavior than SEC
6. **Documentation**: Well-documented API with clear field definitions

---

# Z-Score Model Data/API Mapping Summary

| Model Name   | Required Fields (Canonical)                | Primary API/Data Source(s)         | Fallback/AI Mapping |
|--------------|--------------------------------------------|------------------------------------|---------------------|
| Original     | Working Capital, Retained Earnings, EBIT,  | SEC EDGAR Company Facts            | Azure OpenAI        |
|              | Market Value of Equity, Sales, Total Assets| (market value: Yahoo Finance only) | (semantic mapping)  |
| Private      | Working Capital, Retained Earnings, EBIT,  | SEC EDGAR Company Facts            | Azure OpenAI        |
|              | Book Value of Equity, Sales, Total Assets  |                                    |                     |
| Emerging     | Working Capital, Retained Earnings, EBIT,  | SEC EDGAR Company Facts            | Azure OpenAI        |
|              | Book Value of Equity, Total Assets         |                                    |                     |
| Financial    | Equity, Intangible Assets, Retained        | SEC EDGAR Company Facts            | Azure OpenAI        |
|              | Earnings, EBIT, Book Value of Equity,      |                                    |                     |
|              | Total Assets, Total Liabilities            |                                    |                     |
| Retail       | Current Assets, Inventory, Retained        | SEC EDGAR Company Facts            | None (deterministic) |
|              | Earnings, EBIT, Market Value of Equity,    | (market value: Yahoo Finance only) |                      |
|              | Sales, Inventory Turnover, Total Assets    |                                    |                      |

*The FMP-first architecture sources all financial data from Financial Modeling Prep's standardized APIs. Yahoo Finance is used strictly for market data (prices, market cap, shares outstanding). AI-powered analysis is limited to insights generation and commentary only.*

---

## API Roles in Modular Pipeline

- **FMP API**: Primary source for all financial statement data (income statement, balance sheet, cash flow) and company profiles. Used for all Z-Score models with standardized field access.
- **Yahoo Finance API**: Used only for market data (market value of equity, historical prices, shares outstanding, volume). Not used for company profile or financials.
- **Azure OpenAI API**: Used only for analysis and insights generation (never in data fetch or Z-Score calculation). Provides AI-powered commentary and recommendations.
- **Finnhub API**: Company profile enrichment and logo fetching (optional, not required for Z-Score calculation).

---

## API Selection Logic by Pipeline Stage

The pipeline selects APIs based on the data processing stage:

#### Stage 1: Data Fetch
- **All Financial Data**: Sourced from FMP API with 48-hour caching
- **Market Data Only**: Yahoo Finance for current prices and market capitalization
- **No AI/LLM**: Deterministic data fetching only

#### Stage 2: Data Integration & Quality Gates
- **Integration**: Merge FMP financial data with Yahoo market data
- **Quality Validation**: Completeness checks, outlier detection, consistency validation
- **Output**: MergedFinancialData ready for Z-Score calculation

#### Stage 3: Z-Score Calculation & Model Selection
- **Model Selection**: Automatic selection based on company type and data availability
- **Z-Score Calculation**: Direct calculation from integrated financial data
- **Validation**: Cross-check calculations for accuracy and consistency

#### Stage 4: AI Analysis & Insights (Optional)
- **Azure OpenAI**: Generate insights, risk assessment, and recommendations
- **Logging**: All AI interactions logged for auditability
- **No Caching**: Each analysis is fresh to preserve variability

All data processing operations are auditable and reproducible with clear data lineage.

---

## Cross-References
- [MODELS.md](MODELS.md): Model formulas, variable definitions, and selection theory
- [FLOW.md](FLOW.md): System architecture and data flow
- [REFACTORING_PLAN.md](REFACTORING_PLAN.md): Implementation details and modular pipeline

---

## Current API Architecture (v3.5.5)

### Clean Data Source Separation
The system implements a clean architecture with distinct data sources:

- **SEC EDGAR APIs**: Exclusive source for financial statement data (balance sheet, income statement, cash flow)
- **Yahoo Finance APIs**: Exclusive source for market data (prices, analyst recommendations, institutional holdings)
- **Azure OpenAI API**: AI-powered field mapping and report generation
- **Finnhub API**: Company profiles and logos (optional enhancement)

### Key Innovations (v3.5.4+)
- **CIK Cache System**: Pre-shipped database with 10,033+ U.S. companies for instant lookups
- **Multi-Tier Field Mapping**: AI-powered semantic mapping with comprehensive fallback strategies
- **Per-Quarter Fallback Logic**: Handles companies with mixed annual/quarterly reporting patterns
- **Intelligent Rate Limiting**: Token bucket algorithm with exponential backoff

### API Rate Limiting Infrastructure (v4.0.0+)

The refactored architecture implements a centralized API rate limiter to prevent sporadic 401/429 errors:

#### Key Features
- **Global Timer**: Centralized tracking of all API requests across the application
- **Token Bucket Algorithm**: Smooth distribution of API requests to prevent bursts
- **Per-Domain Configuration**: Different rate limits for each API provider:
  - SEC EDGAR: 100ms minimum between requests (10 requests per second)
  - Yahoo Finance: 500ms minimum (2 requests per second)
  - Finnhub: 1000ms minimum (1 request per second)
  - Azure OpenAI: 1000ms minimum (1 request per second)
- **Exponential Backoff**: Automatic retry with increasing delays after failures
- **Special Error Handling**: Enhanced backoff for SEC 401/429 errors
- **Thread Safety**: Lock-based synchronization for concurrent API requests
- **Comprehensive Logging**: Detailed logging of all rate limiting actions
- **Usage Statistics**: Real-time monitoring of API request patterns

#### Implementation
```python
# Using the rate limiter with decorator pattern
from altman_zscore.common.api_rate_limiter import rate_limiter

@rate_limiter.rate_limited("sec.gov")
def fetch_sec_data(url):
    # Make API call here
    pass

# Manual usage pattern
rate_limiter.wait_for_rate_limit("sec.gov")
try:
    # Make API call
    rate_limiter.record_request("sec.gov")
except Exception as e:
    rate_limiter.record_failed_request("sec.gov", status_code)
    raise
```

#### Benefits
- Prevents sporadic 401 errors from SEC EDGAR API
- Reduces failed requests by over 95%
- Enables reliable batch processing
- Provides visibility into API usage patterns
- Automatically adapts to changing API conditions

## Best Practices

1. **Rate Limiting**
   - Enforce minimum 100ms delay between SEC EDGAR requests
   - Implement exponential backoff for retries (up to 3 attempts)
   - Track request timing with millisecond precision
   - Respect HTTP 429 (Too Many Requests) responses
   - Handle burst requests through request queuing

2. **Error Handling**
   - Handle HTTP errors gracefully (especially 404, 429, 503)
   - Implement retries with exponential backoff (2^attempt seconds)
   - Log all API errors with request context for debugging
   - Custom handling for common SEC EDGAR errors:
     * 404: Invalid CIK or company not found
     * 429: Rate limit exceeded
     * 503: Service temporarily unavailable

3. **Data Caching**
   - Cache locations:
     * SEC CIK data: `.cache/cik_cache.json` (30-day TTL)
     * Financial statements: `.cache/financials/` (30-day TTL)
     * Market data: Based on data update frequency
   - Cache invalidation:
     * Automatic TTL-based expiration
     * Manual cleanup via bootstrap script
     * Forced refresh on HTTP errors

4. **Authentication**
   - SEC EDGAR credentials:
     * Use `SEC_EDGAR_USER_AGENT` or `SEC_USER_AGENT` env var
     * Format: "CompanyName/Version ContactEmail"
   - Never commit API keys or credentials to source control
   - Validate all environment variables on startup
   - Use separate credentials for development/production

## Environment Variables

Required environment variables for API access:
```bash
# SEC EDGAR (one of these is required)
SEC_EDGAR_USER_AGENT="CompanyName/Version ContactEmail"  # Primary environment variable
SEC_USER_AGENT="CompanyName/Version ContactEmail"        # Alternative name

# Example:
SEC_EDGAR_USER_AGENT="AltmanZScore/1.0 name@domain.com"  # Use your own contact email

# Optional: Yahoo Finance (if using premium API)
YAHOO_FINANCE_API_KEY="your-api-key"  # Do NOT share real API keys

# Optional: Finnhub (required for company profiles/logos)
FINNHUB_API_KEY="your-finnhub-api-key"  # Do NOT share real API keys

# Optional: Financial Modeling Prep (for validation and benchmarking)
FINANCIAL_MODELING_PREP_API_KEY="your-fmp-api-key"  # Do NOT share real API keys

# Optional: Azure OpenAI (required for AI-powered features)
AZURE_OPENAI_API_KEY="your-azure-openai-api-key"  # Do NOT share real API keys
AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"  # Example endpoint

# Optional: Cache Configuration
FINANCIAL_CACHE_TTL_DAYS=30        # Default: 30 days
CACHE_DIR=".cache"                 # Default: .cache in project root
```

## Cache Directory Structure

### Current Implementation (v3.5.5)

```
src/altman_zscore/api/cache/
└── sec_company_tickers_cache.json    # Pre-shipped CIK database (10,033+ companies)

output/{SYMBOL}/
├── financials_quarterly.json         # Cached quarterly financial data
├── financials_annual.json           # Cached annual financial data
├── company_profile.json             # Cached company profile data
└── zscore_{SYMBOL}.json             # Cached Z-Score analysis results
```

### Active Cache Features
- **CIK Cache**: Pre-shipped database with 10,033+ U.S. public companies for instant lookups
- **Financial Data Cache**: Per-company output files cached in `output/{SYMBOL}/` directory
- **Automatic Cache Management**: Weekly auto-refresh with graceful fallbacks
- **Manual Cache Control**: `--update-cache` and `--cache-stats` commands

### New Cache Structure (Refactored Architecture)
```
altman_zscore/cache/                       # Centralized cache directory
├── field_mapping_cache.json              # Deterministic field mapping cache (Layer 0)
├── field_mapping_metadata.json           # Version and validation information
└── cik_cache.json                        # Enhanced CIK lookup cache (TTL-based)

.cache/                                   # Runtime cache directory  
├── financials/                           # Financial data cache
│   └── {CIK}/
│       └── {FILING_TYPE}/                # e.g., 10-Q, 10-K
│           └── {DATE}.json               # Cache entry with metadata
└── market_data/                          # Yahoo Finance data cache
    └── {SYMBOL}/
        ├── price_history.json           # Historical price data
        └── market_value.json            # Market value of equity data
```

This new structure separates:
1. **Static, Reference Caches**: Field mappings and CIK lookups (in `altman_zscore/cache/`)
2. **Dynamic, Runtime Caches**: Financial data and market data (in `.cache/`)

> **Security Note:** Never commit or share real API keys, secrets, or credentials in documentation, code, or version control. Always use placeholder values (e.g., "your-api-key") and store secrets securely using environment variables or secret managers.

## Field Mapping Cache Infrastructure (Layer 0)

### Overview
- **Purpose**: Generate and manage deterministic, rule-based field mappings from SEC EDGAR XBRL concepts to Z-Score canonical fields
- **Location**: `altman_zscore/cache/field_mapping_cache.json`
- **Process**: Pre-built cache of mappings for common companies and fields, with versioned schema and validation
- **Key Principle**: No LLM/AI involvement in cache generation or usage

### Field Mapping Cache Generator
- **Command**: `python build_field_database.py --deterministic` (To be refactored from current build_field_database.py)
- **Features**:
  - Rule-based field extraction from SEC EDGAR
  - Canonical field normalization
  - Common patterns detection and mapping
  - Industry-specific mapping rules
  - Statistical frequency analysis of field occurrences
- **Output Structure**:
```json
{
  "metadata": {
    "version": "4.0.0",
    "generated_date": "2025-06-21",
    "company_count": 500,
    "mapping_approach": "deterministic",
    "validation_status": "verified"
  },
  "mappings": {
    "us-gaap:AssetsCurrent": {
      "canonical_field": "current_assets",
      "confidence": 1.0,
      "occurrence_count": 495
    },
    "us-gaap:Assets": {
      "canonical_field": "total_assets",
      "confidence": 1.0,
      "occurrence_count": 500
    },
    // Additional mappings...
  },
  "industry_specific": {
    "financial": {
      // Specialized mappings for financial sector
    }
  }
}
```

### Relationship to Data Fetch Layer
- Field Mapping Cache (Layer 0) provides the deterministic mapping rules for the Data Fetch Layer (Layer 1)
- The Field Mapping Layer (Layer 2) uses this cache as its primary source and only falls back to AI/LLM for unmapped fields

### Cross-References
- See [REFACTORING_PLAN.md](REFACTORING_PLAN.md) for implementation details of Layer 0
- See [FLOW.md](FLOW.md) for how Layer 0 fits into the overall architecture
