"""
FMP Financial Data Cache Layer

This layer is responsible for caching and managing FMP (Financial Modeling Prep) API data
for efficient access and reduced API calls. It handles storage and retrieval of financial
statements (income statement, balance sheet, cash flow, ratios) for companies.

Key Features:
- Per-company financial data caching
- Atomic write operations with data validation
- TTL-based cache expiration
- Thread-safe operations
- Data integrity validation
"""

# Core modules
from .cache_manager import (
    store_financial_data,
    load_financial_data,
    get_cache_info,
    validate_cache_integrity,
    get_default_cache_dir
)
from .validation import validate_financial_data

__all__ = [
    'store_financial_data', 
    'load_financial_data',
    'get_cache_info',
    'validate_cache_integrity',
    'get_default_cache_dir',    'validate_financial_data'
]
