"""
FMP Data Fetcher - Layer 1

Financial Modeling Prep (FMP) API data fetcher with 48-hour caching.
All API calls are cached to prevent redundant downloads within the TTL period.

This fetcher handles:
- Income statements
- Balance sheets  
- Cash flow statements
- Financial ratios
- Company information

Key Features:
- 48-hour cache TTL for all FMP API calls
- Rate limiting integration
- Error handling and retries
- Data validation
"""

import os
import requests
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

from ...common.logging_config import get_logger
from ...common.config import get_config
from ...common.cache import get_cache, CacheBackend  
# from ...common.api_rate_limiter import rate_limiter
from ...common.exceptions import DataFetchError, ValidationError
from ...cache.cache_manager import store_financial_data, load_financial_data

logger = get_logger(__name__)

# Cache TTL: 48 hours (in seconds)
CACHE_TTL_SECONDS = 48 * 60 * 60

# FMP API base URL
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"


@dataclass
class FMPConfig:
    """FMP API configuration."""
    api_key: str
    base_url: str = FMP_BASE_URL
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'FMPConfig':
        """Create config from environment variables."""
        api_key = os.getenv("FINANCIAL_MODELING_PREP_API_KEY")
        
        if not api_key:
            raise DataFetchError("FINANCIAL_MODELING_PREP_API_KEY environment variable is required")
        
        return cls(api_key=api_key)


class FMPDataFetcher:
    """
    Financial Modeling Prep API data fetcher with caching.
    
    All API calls are cached for 48 hours to prevent redundant downloads.
    Uses rate limiting to respect API limits.
    """
    def __init__(self, config: Optional[FMPConfig] = None):
        """
        Initialize FMP data fetcher.
        
        Args:
            config: Optional FMP configuration (defaults to environment config)
        """
        self.config = config or FMPConfig.from_env()
        self.cache = get_cache("fmp_api", backend=CacheBackend.FILE, cache_dir=".cache/fmp")
        self.session = requests.Session()
        
        logger.info(f"Initialized FMP data fetcher with base URL: {self.config.base_url}")
      # @rate_limiter.rate_limited("financialmodelingprep.com")
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make rate-limited request to FMP API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            
        Returns:
            API response data
            
        Raises:
            APIError: If request fails or returns invalid data
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        # Add API key to params
        if params is None:
            params = {}
        params['apikey'] = self.config.api_key
        
        logger.debug(f"Making FMP API request: {url}")
        
        # Basic rate limiting - 0.5 seconds between requests (2 requests per second)
        time.sleep(0.5)
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                  # Check for FMP API errors
                if isinstance(data, dict) and 'Error Message' in data:
                    raise DataFetchError(f"FMP API error: {data['Error Message']}")
                
                if not data:
                    raise DataFetchError("Empty response from FMP API")
                
                logger.debug(f"FMP API request successful: {len(data) if isinstance(data, list) else 'dict'} items")
                return data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"FMP API request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise DataFetchError(f"FMP API request failed after {self.config.max_retries} attempts: {e}")
                  # Exponential backoff
                time.sleep(2 ** attempt)

    def get_income_statement(self, symbol: str, period: str = "annual") -> List[Dict[str, Any]]:
        """
        Get income statement data from FMP API with caching.
        
        Uses API default limit (depends on plan: free=5, paid=up to 30).
        
        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            
        Returns:
            List of income statement data
        """
        cache_key = f"fmp_income:{symbol}:{period}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached income statement for {symbol}")
            return cached_result
        
        # Fetch from API (let API use default limit based on plan)
        endpoint = f"income-statement/{symbol}"
        params = {
            'period': period
        }
        
        result = self._make_request(endpoint, params)
          # Cache result
        self.cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS)
        
        return result
    
    def get_balance_sheet(self, symbol: str, period: str = "annual") -> List[Dict[str, Any]]:
        """
        Get balance sheet data from FMP API with caching.
        
        Uses API default limit (depends on plan: free=5, paid=up to 30).
        
        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            
        Returns:
            List of balance sheet data
        """
        cache_key = f"fmp_balance:{symbol}:{period}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached balance sheet for {symbol}")
            return cached_result
        
        # Fetch from API (let API use default limit based on plan)
        endpoint = f"balance-sheet-statement/{symbol}"
        params = {
            'period': period
        }
          result = self._make_request(endpoint, params)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS)
        
        return result
    
    def get_cash_flow(self, symbol: str, period: str = "annual") -> List[Dict[str, Any]]:
        """
        Get cash flow statement data from FMP API with caching.
        
        Uses API default limit (depends on plan: free=5, paid=up to 30).
        
        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            
        Returns:
            List of cash flow data
        """
        cache_key = f"fmp_cashflow:{symbol}:{period}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached cash flow for {symbol}")
            return cached_result
        
        # Fetch from API (let API use default limit based on plan)
        endpoint = f"cash-flow-statement/{symbol}"
        params = {
            'period': period
        }
        
        result = self._make_request(endpoint, params)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS)
        
        return result
    
    def get_financial_ratios(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get financial ratios data from FMP API with caching.
        
        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch
            
        Returns:
            List of financial ratios data
        """
        cache_key = f"fmp_ratios:{symbol}:{period}:{limit}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached financial ratios for {symbol}")
            return cached_result
        
        # Fetch from API
        endpoint = f"ratios/{symbol}"
        params = {
            'period': period,
            'limit': limit
        }
        
        result = self._make_request(endpoint, params)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS)
        
        return result
    
    def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """
        Get company profile data from FMP API with caching.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Company profile data
        """
        cache_key = f"fmp_profile:{symbol}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached company profile for {symbol}")
            return cached_result
        
        # Fetch from API
        endpoint = f"profile/{symbol}"
        result = self._make_request(endpoint)
        
        # Return first item if it's a list
        if isinstance(result, list) and result:
            result = result[0]
        
        # Cache result
        self.cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS)
        
        return result
    
    def get_complete_financial_data(self, symbol: str, period: str = "annual", limit: int = 5) -> Dict[str, Any]:
        """
        Get complete financial data for a symbol (all statements + ratios).
        
        This method orchestrates multiple API calls and combines the results.
        Each individual API call is cached for 48 hours.
        
        Args:
            symbol: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to fetch
            
        Returns:
            Complete financial data dictionary
        """
        logger.info(f"Fetching complete financial data for {symbol} ({period}, limit={limit})")
        
        # Check if we have cached complete data first
        try:
            cached_data = load_financial_data(symbol)
            if cached_data:
                logger.info(f"Using cached complete financial data for {symbol}")
                return cached_data
        except Exception as e:
            logger.debug(f"No cached complete data for {symbol}: {e}")
        
        # Fetch all data components (each call is individually cached)
        financial_data = {}
        
        try:
            financial_data['income_statement'] = self.get_income_statement(symbol, period, limit)
            logger.debug(f"Fetched income statement for {symbol}: {len(financial_data['income_statement'])} periods")
        except Exception as e:
            logger.error(f"Failed to fetch income statement for {symbol}: {e}")
            financial_data['income_statement'] = []
        
        try:
            financial_data['balance_sheet'] = self.get_balance_sheet(symbol, period, limit)
            logger.debug(f"Fetched balance sheet for {symbol}: {len(financial_data['balance_sheet'])} periods")
        except Exception as e:
            logger.error(f"Failed to fetch balance sheet for {symbol}: {e}")
            financial_data['balance_sheet'] = []
        
        try:
            financial_data['cash_flow'] = self.get_cash_flow(symbol, period, limit)
            logger.debug(f"Fetched cash flow for {symbol}: {len(financial_data['cash_flow'])} periods")
        except Exception as e:
            logger.error(f"Failed to fetch cash flow for {symbol}: {e}")
            financial_data['cash_flow'] = []
        
        try:
            financial_data['ratios'] = self.get_financial_ratios(symbol, period, limit)
            logger.debug(f"Fetched ratios for {symbol}: {len(financial_data['ratios'])} periods")
        except Exception as e:
            logger.error(f"Failed to fetch ratios for {symbol}: {e}")
            financial_data['ratios'] = []
        
        try:
            financial_data['profile'] = self.get_company_profile(symbol)
            logger.debug(f"Fetched company profile for {symbol}")
        except Exception as e:
            logger.error(f"Failed to fetch company profile for {symbol}: {e}")
            financial_data['profile'] = {}
        
        # Store complete data in cache
        try:
            store_financial_data(symbol, financial_data, validate_before_store=False)
            logger.info(f"Stored complete financial data for {symbol} in cache")
        except Exception as e:
            logger.warning(f"Failed to store complete financial data for {symbol}: {e}")
        
        return financial_data
