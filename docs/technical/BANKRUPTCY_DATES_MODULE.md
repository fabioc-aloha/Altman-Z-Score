# Bankruptcy Dates Module Documentation

**Implementation Date:** July 6, 2025  
**Version:** 1.0  
**Path:** `altman_zscore/data/bankruptcy_dates.py`

## Overview

The Bankruptcy Dates module serves as the foundation for the bankruptcy analysis framework, providing a comprehensive database of historical bankruptcy dates and utility functions for working with bankrupt companies. This module enables detailed analysis of financial health metrics in the quarters leading up to bankruptcy, validating the predictive capabilities of various Z-Score models.

## Key Components

### 1. Bankruptcy Database

The module maintains a categorized database of bankruptcy dates:

```python
BANKRUPTCY_DATES = {
    # Retail Bankruptcies
    'TOY': '2017-09-18',    # Toys"R"Us
    'SHLDQ': '2018-10-15',  # Sears Holdings
    'JCPNQ': '2020-05-15',  # JCPenney
    # ... more retail entries ...
    
    # Energy Sector Bankruptcies
    'DNOW': '2020-06-22',   # Diamond Offshore
    'WLL': '2020-04-01',    # Whiting Petroleum
    'CHK': '2020-06-28',    # Chesapeake Energy
    
    # Other Notable Bankruptcies
    'LATAM': '2020-05-26',  # LATAM Airlines
    'HTZ': '2020-05-22',    # Hertz
    # ... more entries ...
}
```

### 2. Core Utility Functions

#### `get_bankruptcy_date(ticker: str) -> Optional[datetime]`

Retrieves the bankruptcy date for a specific ticker:
- Returns a datetime object if the company is in the database
- Returns None if the company is not in the database
- Used to set end_date filters for financial data fetching

#### `is_bankrupt_company(ticker: str) -> bool`

Checks if a company has a bankruptcy record:
- Returns True if the ticker is in the database
- Returns False otherwise
- Used for conditional bankruptcy analysis activation

#### `get_all_bankrupt_tickers() -> list`

Returns a list of all tickers in the bankruptcy database:
- Enables batch processing of all bankrupt companies
- Used by the `run_bankruptcy_analysis()` method in the main pipeline

## Integration Points

The bankruptcy dates module integrates with several key components of the Altman Z-Score system:

1. **Main Pipeline Integration**
   - `analyze_ticker()` method accepts bankruptcy_analysis parameter
   - `run_bankruptcy_analysis()` method processes all bankrupt companies
   
2. **Data Fetching Layer**
   - `data_merger.py` uses bankruptcy dates to set end_date filters
   - `yahoo_fetcher.py` retrieves historical market data for correlation analysis
   
3. **Output Generation**
   - `report_generator.py` creates specialized bankruptcy analysis sections
   - `dashboard_generator.py` produces visualizations with bankruptcy markers
   - `trend_analysis.py` enhances charts with pre-bankruptcy highlighting

## Usage Patterns

### Individual Company Analysis

```python
from altman_zscore.main_pipeline import AltmanZScorePipeline

pipeline = AltmanZScorePipeline()
result = await pipeline.analyze_ticker(
    "SHLDQ",  # Sears Holdings
    bankruptcy_analysis=True,
    pre_bankruptcy_quarters=3
)
```

### Batch Bankruptcy Analysis

```python
from altman_zscore.main_pipeline import AltmanZScorePipeline

pipeline = AltmanZScorePipeline()
results = await pipeline.run_bankruptcy_analysis(
    pre_bankruptcy_quarters=3,
    generate_charts=True,
    generate_reports=True
)
```

### Direct Module Usage

```python
from altman_zscore.data.bankruptcy_dates import (
    get_bankruptcy_date,
    is_bankrupt_company,
    get_all_bankrupt_tickers
)

# Check if company has bankruptcy record
if is_bankrupt_company("SHLDQ"):
    # Get the bankruptcy date
    bankruptcy_date = get_bankruptcy_date("SHLDQ")
    print(f"Sears filed for bankruptcy on {bankruptcy_date.strftime('%Y-%m-%d')}")
    
# Get all bankrupt companies
tickers = get_all_bankrupt_tickers()
print(f"Total companies in bankruptcy database: {len(tickers)}")
```

## Command-Line Interface

The bankruptcy analysis functionality is accessible through the main CLI:

```bash
# Analyze a specific bankrupt company
python main.py --bankruptcy-analysis SHLDQ

# Analyze all companies in the bankruptcy database
python main.py --run-bankruptcy-analysis --quarters 3
```

## Implementation Benefits

1. **Predictive Model Validation**: Validates how effectively different Z-Score models predict bankruptcy
2. **Warning Sign Identification**: Reveals early financial warning signs that precede bankruptcy
3. **Market Correlation Analysis**: Correlates market metrics with Z-Score deterioration
4. **Academic Research Support**: Provides structured data for academic research on bankruptcy prediction
5. **Investor Education**: Creates visual examples of financial deterioration patterns

## Future Enhancements

1. **Expanded Database**: Add more international companies and additional sectors
2. **Predictive Modeling**: Develop machine learning models based on pre-bankruptcy patterns
3. **Cross-Model Comparison**: Compare Z-Score against other bankruptcy prediction models
4. **Industry-Specific Analysis**: Develop specialized analysis for each industry sector
5. **Warning Sign Cataloging**: Create a comprehensive catalog of pre-bankruptcy warning signs
