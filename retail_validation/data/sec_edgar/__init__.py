"""
SEC EDGAR Integration for Retail Validation Framework
===================================================

This package provides functionality for retrieving and parsing 
historical financial data from SEC EDGAR filings for delisted companies.

Components:
- edgar_connector.py: Main connector to SEC EDGAR system
- filing_parser.py: Extracts financial data from SEC filings
- cik_ticker_map.json: Maps tickers to SEC CIK numbers

Usage:
```python
from retail_validation.data.sec_edgar.edgar_connector import EdgarConnector

# Initialize connector
edgar = EdgarConnector()

# Get financial data for a delisted company
data = await edgar.get_financial_data("SHLDQ")  # Sears Holdings
```
"""

__all__ = ['EdgarConnector', 'FilingParser']

from .edgar_connector import EdgarConnector
from .filing_parser import FilingParser
