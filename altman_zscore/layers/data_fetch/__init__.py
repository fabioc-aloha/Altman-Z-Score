"""
Data Fetch Layer - Layer 1

This layer is responsible for fetching financial data from external APIs with caching.
All API calls (except LLM) are cached with 48-hour TTL to prevent redundant downloads.

Available modules:
- fmp_fetcher: Financial Modeling Prep API data (CACHED)
- yahoo_fetcher: Yahoo Finance market data (CACHED)
- llm_client: Azure OpenAI LLM interactions (NOT CACHED - saves prompts/responses)
- data_merger: Combines FMP and Yahoo data (Data Integration & Quality Gates)
- quality_gates: Comprehensive data validation and quality assurance
"""

from .fmp_fetcher import FMPDataFetcher
from .yahoo_fetcher import YahooDataFetcher
from .llm_client import LLMClient
from .data_merger import DataMerger, merge_financial_data, validate_data_completeness
from .quality_gates import QualityGates, validate_financial_data_integrity

__all__ = [
    'FMPDataFetcher',
    'YahooDataFetcher', 
    'LLMClient',
    'DataMerger',
    'merge_financial_data',
    'validate_data_completeness',
    'QualityGates', 
    'validate_financial_data_integrity'
]
