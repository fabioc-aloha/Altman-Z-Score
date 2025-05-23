# APIs Documentation

This document provides details about the external APIs used in the Altman Z-Score project.

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

### XBRL Data APIs
- **Base URLs**:
  - Company Concept: `https://data.sec.gov/api/xbrl/companyconcept`
  - Company Facts: `https://data.sec.gov/api/xbrl/companyfacts`
  - Frames: `https://data.sec.gov/api/xbrl/frames`
- **Endpoints**:
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
SEC_EDGAR_USER_AGENT="AltmanZScore/1.0 name@domain.com"

# Optional: Yahoo Finance (if using premium API)
YAHOO_FINANCE_API_KEY="your-api-key"

# Optional: Cache Configuration
FINANCIAL_CACHE_TTL_DAYS=30        # Default: 30 days
CACHE_DIR=".cache"                 # Default: .cache in project root
```

## Cache Directory Structure

```
.cache/
├── cik_cache.json            # CIK lookup cache (30-day TTL)
└── financials/              # Financial data cache
    └── {CIK}/
        └── {FILING_TYPE}/   # e.g., 10-Q, 10-K
            └── {DATE}.json  # Cache entry with metadata
```
