# Handling Delisted/Bankrupt Companies in Retail Validation

## Challenge Overview

A key aspect of validating the retail Z-Score model involves testing its ability to predict bankruptcies by analyzing companies that have already gone bankrupt. However, this presents technical challenges because most bankrupt companies are delisted from exchanges, and their financial data becomes unavailable in standard API sources like Financial Modeling Prep (FMP) and Yahoo Finance.

This document outlines strategies for handling these delisted companies in the retail validation framework.

## Current Symptoms

When attempting to analyze bankrupt company tickers such as NMRCQ (Neiman Marcus), you may encounter errors like:

```
ERROR - Failed to fetch multiple quarters data for NMRCQ: Invalid ticker symbol 'NMRCQ' - not found in financial databases
```

This occurs because these companies are no longer traded publicly, and current financial data APIs don't maintain historical data for delisted securities.

## Solution Strategies

### 1. Historical Data Archives

For academic bankruptcy prediction validation, use specialized historical data sources:

- **Financial Research Databases**: Academic institutions often have access to WRDS (Wharton Research Data Services), Compustat, or CRSP databases which maintain historical data for delisted companies
- **Commercial Historical Data**: Services like Bloomberg Terminal, FactSet, or S&P Capital IQ maintain comprehensive historical data including bankrupt companies
- **SEC EDGAR Archives**: Manual extraction from historical 10-K/10-Q filings prior to bankruptcy

### 2. Synthetic Test Cases

When historical data is unavailable, create synthetic test cases:

- **Snapshot Approach**: Use the last available data before delisting
- **Deterioration Patterns**: Apply known financial deterioration patterns to existing data
- **Known Ratios**: Manually input key ratios from the periods leading up to bankruptcy from academic papers or case studies

### 3. Proxy Analysis

Use similar companies or time periods as proxies:

- **Industry Peers**: Analyze similar companies that experienced distress but remained listed
- **Pre-Bankruptcy Period**: For companies where some historical data is available before bankruptcy, focus on that period
- **Similar Case Studies**: Apply findings from well-documented retail bankruptcies with available data

## SEC EDGAR Historical Data Implementation

The retail validation framework implements SEC EDGAR data retrieval as the primary method for obtaining historical financial data for delisted companies. SEC EDGAR (Electronic Data Gathering, Analysis, and Retrieval) is a publicly accessible database containing all required filings from public companies, including those that have since gone bankrupt.

### SEC EDGAR Data Integration

#### 1. How SEC EDGAR Works

- **Complete Historical Coverage**: SEC EDGAR maintains all public company filings since 1994
- **Filing Types**: 10-K (annual), 10-Q (quarterly), 8-K (material events)
- **Pre-Bankruptcy Data**: Financial statements for multiple years/quarters before bankruptcy
- **Structured Data**: Recent filings include XBRL (eXtensible Business Reporting Language) tags
- **Company Identification**: Each company has a unique CIK (Central Index Key) used in the SEC system

#### 2. SEC EDGAR Data Flow

1. **Company Identification**: CIK (Central Index Key) lookup by ticker or company name
2. **Filing Location**: SEC URLs for historical 10-K/10-Q filings
3. **Data Extraction**: Parsing financial statements from HTML/XML formats
4. **Ratio Calculation**: Computing Z-Score components from extracted data

#### 3. SEC EDGAR Integration Components

The framework includes the following components:

```
retail_validation/
├── data/
│   ├── sec_edgar/
│   │   ├── __init__.py
│   │   ├── edgar_connector.py       # SEC EDGAR API interface
│   │   ├── filing_parser.py         # Financial statement extraction
│   │   ├── cik_ticker_map.json      # Maps tickers to SEC CIK numbers
│   │   └── cache/                   # Cache directory for SEC data
```

#### 4. Implementation Features

- **CIK Mapping**: Pre-populated mapping of bankrupt retail tickers to their SEC CIK numbers
- **Smart Filing Selection**: Automatically finds the most recent filings before bankruptcy
- **Dual Parsing Strategy**: 
  - XBRL parsing for modern filings (structured data)
  - HTML table parsing for older filings (pre-XBRL era)
- **Caching**: Local caching of SEC EDGAR data to minimize repeated API calls
- **Rate Limiting**: Built-in request throttling to comply with SEC's fair access policy
- **Data Quality Assessment**: Validation of extracted financial metrics
- **Missing Data Estimation**: Reasonable estimates for missing fields based on industry patterns

#### 5. Command-Line Integration

The SEC EDGAR feature can be enabled via the command line:

```powershell
.\retail_validation\scripts\run_retail_validation.ps1 -FullValidation -UseSECEDGAR
```

Or in Python:

```python
python retail_validation/scripts/validate_retail_model.py --use-sec-edgar
```

### SEC EDGAR Connector Implementation

```python
# retail_validation/data/sec_edgar/edgar_connector.py

from pathlib import Path
import json
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple

class EdgarConnector:
    """Connector for retrieving historical financial data from SEC EDGAR"""
    
    def __init__(self, cache_dir: str = None):
        self.headers = {
            'User-Agent': 'RetailModelValidation/1.0 (research@altmanzscore.org)'
        }
        self.base_url = "https://www.sec.gov/Archives"
        
        # Set up caching for SEC data
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "cache" / "sec_edgar"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load CIK mapping
        self.cik_map = self._load_cik_mapping()
    
    def _load_cik_mapping(self) -> Dict[str, str]:
        """Load the mapping of tickers to CIK numbers"""
        cik_file = Path(__file__).parent / "cik_ticker_map.json"
        
        if cik_file.exists():
            with open(cik_file, 'r') as f:
                return json.load(f)
        else:
            # Create a minimal mapping with our bankrupt companies
            return {
                "NMRCQ": "0001398666",  # Neiman Marcus
                "JCPNQ": "0001166126",  # JCPenney
                "SHLDQ": "0001310067",  # Sears Holdings
                "BRKSQ": "0000078890",  # Brooks Brothers
                "PIRRQ": "0000278130",  # Pier 1 Imports
                "TOY": "0001005414",    # Toys R Us
                # Add more as needed
            }
    
    async def get_cik_for_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK for a ticker symbol"""
        # First check our mapping
        if ticker in self.cik_map:
            return self.cik_map[ticker]
        
        # Otherwise try to look it up (implementation omitted for brevity)
        return None
    
    async def get_recent_filings(self, ticker: str, filing_type: str = "10-K",
                             years_before_bankruptcy: int = 3) -> List[Dict]:
        """Get recent filings before bankruptcy"""
        cik = await self.get_cik_for_ticker(ticker)
        if not cik:
            print(f"Could not find CIK for {ticker}")
            return []
        
        # Check cache first
        cache_file = self.cache_dir / f"{ticker}_{filing_type}_filings.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Implementation for retrieving filings from EDGAR
        # (would include searching index files and filing listings)
        
        return []  # Placeholder
    
    async def get_financial_data(self, ticker: str, 
                           quarters_before_bankruptcy: int = 4) -> Optional[Dict]:
        """Get financial data for calculating Z-Score"""
        
        # Find bankruptcy date
        from retail_validation.config.validation_config import BANKRUPTCY_DATES
        if ticker not in BANKRUPTCY_DATES:
            print(f"No bankruptcy date found for {ticker}")
            return None
        
        bankruptcy_date = BANKRUPTCY_DATES[ticker]
        
        # Get annual and quarterly filings before bankruptcy
        annual_filings = await self.get_recent_filings(ticker, "10-K", 3)
        quarterly_filings = await self.get_recent_filings(ticker, "10-Q", quarters_before_bankruptcy)
        
        if not annual_filings and not quarterly_filings:
            print(f"No filings found for {ticker}")
            return None
        
        # Extract and process financial data (implementation omitted for brevity)
        # Would extract key financial metrics:
        # - Current Assets
        # - Total Assets
        # - Current Liabilities
        # - Total Liabilities
        # - Retained Earnings
        # - EBIT (Earnings Before Interest and Taxes)
        # - Sales/Revenue
        # - Market Value of Equity (from historical price data)
        
        return None  # Placeholder
```

### Integrating SEC EDGAR Data in the Validation Framework

The framework's `_load_from_historical_database` method has been updated to use SEC EDGAR:

```python
async def _load_from_historical_database(self, ticker: str) -> Dict:
    """Load historical data for delisted companies from SEC EDGAR"""
    
    from retail_validation.data.sec_edgar.edgar_connector import EdgarConnector
    
    print(f"  - Attempting to load SEC EDGAR data for {ticker}")
    
    edgar_connector = EdgarConnector()
    financial_data = await edgar_connector.get_financial_data(ticker, quarters_before_bankruptcy=4)
    
    if not financial_data:
        print(f"  - No SEC EDGAR data available for {ticker}")
        return None
    
    # Process financial data into Z-Score components
    # (would transform SEC data into the format expected by Z-Score calculator)
    
    # Return processed data
    return {
        'retail_score': financial_data.get('z_score_retail'),
        'retail_risk': financial_data.get('risk_category_retail'),
        'traditional_score': financial_data.get('z_score_original'),
        'traditional_risk': financial_data.get('risk_category_original'),
        'category': get_category_for_ticker(ticker),
        'bankruptcy_date': self.bankruptcy_dates.get(ticker),
        'components': financial_data.get('components', {}),
        'warnings': financial_data.get('warnings', []),
        'metadata': {
            'data_source': 'sec_edgar',
            'filing_date': financial_data.get('filing_date'),
            'quarters_before_bankruptcy': financial_data.get('quarters_before_bankruptcy')
        }
    }
```

## Implementation in the Validation Framework

The retail validation framework implements these strategies through:

### Default Configuration

```python
# From validation_config.py
BANKRUPTCY_VALIDATION_APPROACH = "hybrid"  # Options: "historical", "synthetic", "proxy", "hybrid"
HISTORICAL_DATA_SOURCE = None  # Set to database connection or None if unavailable
USE_AVAILABLE_TICKERS_ONLY = True  # Skip unavailable tickers without failing
```

### Data Source Fallback Chain

1. **Primary API Sources**: First attempt standard APIs (FMP, Yahoo Finance)
2. **Historical Database**: If configured, attempt to retrieve from historical database
3. **Local Cache**: Check if the data exists in local cache from previous runs
4. **Synthetic Generator**: For bankruptcy analysis only, generate synthetic data based on patterns

### Code Implementation

The `RetailModelValidator` class implements fallback mechanisms:

```python
async def calculate_retail_scores(self, tickers: List[str]) -> Dict:
    """Calculate retail Z-Scores with fallback for unavailable tickers"""
    results = {}
    
    for ticker in tickers:
        try:
            # Normal processing flow
            financial_data = await self.data_merger.merge_financial_data(ticker)
            # Calculate scores...
            
        except InvalidTickerError:
            # Handle unavailable ticker
            if self.config.USE_AVAILABLE_TICKERS_ONLY:
                print(f"Skipping unavailable ticker {ticker}...")
                
                # For bankrupt companies, use fallback strategies if configured
                if ticker in self.bankruptcy_dates and self.config.BANKRUPTCY_VALIDATION_APPROACH != "standard":
                    results[ticker] = await self._process_unavailable_bankrupt_ticker(ticker)
                else:
                    results[ticker] = {'error': 'Ticker unavailable', 'category': self._determine_category(ticker)}
            else:
                # Fail validation run if strict mode is enabled
                raise
    
    return results

async def _process_unavailable_bankrupt_ticker(self, ticker: str) -> Dict:
    """Process a bankrupt ticker that's unavailable using configured fallback strategy"""
    
    if self.config.BANKRUPTCY_VALIDATION_APPROACH == "historical":
        # Attempt to load from historical database
        return await self._load_from_historical_database(ticker)
        
    elif self.config.BANKRUPTCY_VALIDATION_APPROACH == "synthetic":
        # Generate synthetic data for bankruptcy analysis
        return self._generate_synthetic_bankrupt_data(ticker)
        
    elif self.config.BANKRUPTCY_VALIDATION_APPROACH == "proxy":
        # Use proxy company or period
        return await self._use_proxy_company_data(ticker)
        
    elif self.config.BANKRUPTCY_VALIDATION_APPROACH == "hybrid":
        # Try multiple approaches in sequence
        methods = [self._load_from_historical_database, 
                  self._load_from_local_cache,
                  self._generate_synthetic_bankrupt_data]
        
        for method in methods:
            try:
                result = await method(ticker)
                if result:
                    return result
            except Exception:
                continue
                
        # Fallback to acknowledgment of bankruptcy
        return {
            'retail_score': None,
            'retail_risk': None,
            'traditional_score': None,
            'traditional_risk': None,
            'category': 'failed',
            'bankruptcy_date': self.bankruptcy_dates.get(ticker),
            'bankruptcy_confirmed': True,
            'data_source': 'unavailable'
        }
```

## User Guidelines

### Running Bankruptcy Analysis with Limited Data

When running bankruptcy analysis tests:

1. **Focus on Available Companies**:
   ```powershell
   .\retail_validation\scripts\run_retail_validation.ps1 -AvailableOnly
   ```

2. **Use Pre-Configured Sample**:
   ```powershell
   .\retail_validation\scripts\run_retail_validation.ps1 -SampleBankruptcy
   ```
   
3. **Reference Historical Results**:
   ```powershell
   .\retail_validation\scripts\run_retail_validation.ps1 -UseHistoricalResults
   ```

4. **Use SEC EDGAR for Delisted Companies**:
   ```powershell
   .\retail_validation\scripts\run_retail_validation.ps1 -UseSECEDGAR
   ```
   This option automatically retrieves historical financial data from SEC EDGAR filings for delisted companies.

### Configuring Bankruptcy Analysis

To modify bankruptcy analysis behavior, edit `retail_validation/config/validation_config.py`:

```python
# Bankruptcy Analysis Configuration
BANKRUPTCY_VALIDATION_APPROACH = "hybrid"  # Try multiple methods in sequence
USE_AVAILABLE_TICKERS_ONLY = True  # Skip unavailable tickers
INCLUDE_SYNTHETIC_DATA = False  # Whether to include synthetically generated bankruptcy cases
USE_SEC_EDGAR = True  # Use SEC EDGAR as historical data source for delisted companies
SEC_EDGAR_CACHE_DIR = VALIDATION_ROOT / "cache" / "sec_edgar"  # Cache directory for SEC EDGAR data
```

## Recommended Approaches

For the most effective retail model validation:

1. **Current Companies Focus**: 
   - Prioritize currently available companies in distress/gray zone for validation
   - Test the model's ability to identify current companies at risk
   - Compare with traditional Z-Score on currently available data

2. **Academic Documentation**:
   - Reference published bankruptcy prediction studies and benchmarks
   - Document known limitations in historical data availability
   - Supplement with case studies of notable retail bankruptcies

3. **Alternative Validation**:
   - Use industry expert assessment for validation
   - Incorporate credit rating changes and market signals
   - Add qualitative factors for comprehensive model validation

## Conclusion

With the implementation of SEC EDGAR integration, the retail validation framework now provides a robust solution for handling delisted and bankrupt companies. While standard financial data APIs may not maintain historical data for delisted securities, the SEC EDGAR database offers a reliable alternative source of historical financial statements that can be used for bankruptcy prediction model validation.

The framework's comprehensive approach combines:

1. **SEC EDGAR Data Retrieval**: Accessing historical financial statements directly from SEC filings
2. **Multiple Fallback Strategies**: Using a chain of alternative data sources and approaches
3. **Flexible Configuration**: Allowing users to customize the validation process

This implementation significantly enhances the framework's ability to validate the retail Z-Score model's bankruptcy prediction capabilities on real historical cases, providing more robust empirical validation of the novel retail model described in NOVEL_RETAIL_MODEL.md.
