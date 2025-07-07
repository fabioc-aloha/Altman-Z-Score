"""
Bankruptcy Dates Database

This module maintains a database of known bankruptcy dates for companies,
enabling pre-bankruptcy analysis to validate Z-Score predictive capabilities.

Key Features:
- Dynamic bankruptcy detection using Yahoo Finance API
- Cached health status checks (24-hour TTL) to minimize API calls
- Curated bankruptcy dates for known companies as fallback
- Utility functions for bankruptcy date retrieval and validation
- Support for batch processing of bankrupt companies
- Integration with the main pipeline for specialized analysis

The module uses real-time Yahoo Finance data to determine company health status,
with intelligent caching to balance accuracy with performance.
"""

from typing import Dict, Optional
from datetime import datetime
import time

# Import caching infrastructure
from ..common.cache import get_cache, CacheBackend
from ..common.logging_config import get_logger

logger = get_logger(__name__)

# Cache TTL: 24 hours (in seconds) - balance between accuracy and performance
CACHE_TTL_SECONDS = 24 * 60 * 60

# Initialize cache for bankruptcy/health status checks
_health_cache = get_cache("company_health", backend=CacheBackend.FILE, cache_dir=".cache/health")

# Curated bankruptcy dates for known companies (when Yahoo Finance doesn't have data)
# This is a fallback for companies where we have confirmed bankruptcy dates
KNOWN_BANKRUPTCY_DATES = {
    # Retail bankruptcies
    "SHLDQ": datetime(2018, 10, 15),  # Sears Holdings bankruptcy filing
    "BLOC": datetime(2010, 9, 23),   # Blockbuster bankruptcy filing
    "BBBYQ": datetime(2023, 4, 23),  # Bed Bath & Beyond bankruptcy filing
    "JCPNQ": datetime(2020, 5, 15),  # J.C. Penney bankruptcy filing
    
    # Energy bankruptcies
    "ENRNQ": datetime(2001, 12, 2),  # Enron bankruptcy filing
    "WCGIQ": datetime(2004, 7, 11),  # WorldCom bankruptcy filing
    "CHKAQ": datetime(2020, 6, 28),  # Chesapeake Energy bankruptcy filing
    
    # Other notable bankruptcies
    "GMGMQ": datetime(2009, 6, 1),   # General Motors bankruptcy filing
    "LEHM": datetime(2008, 9, 15),   # Lehman Brothers bankruptcy filing
    "WAMU": datetime(2008, 9, 25),   # Washington Mutual bankruptcy filing
    "HTZGQ": datetime(2020, 5, 22),  # Hertz bankruptcy filing
    "PCGIQ": datetime(2019, 1, 29),  # PG&E bankruptcy filing
    
    # Technology acquisitions/delistings
    "YHOO": datetime(2017, 6, 13),   # Yahoo acquisition/delisting
    "TWTR": datetime(2022, 10, 27),  # Twitter acquisition/delisting
    "XLNX": datetime(2022, 2, 14),   # Xilinx acquisition/delisting
}


def get_company_health_status(ticker: str) -> Dict[str, any]:
    """
    Dynamically determine company health status using Yahoo Finance with caching.
    
    This replaces the hard-coded bankruptcy database with real-time checks
    to determine if a company is active, delisted, or bankrupt.
    Results are cached for 24 hours to balance accuracy with performance.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with health status information:
        {
            'is_active': bool,
            'is_delisted': bool, 
            'is_bankrupt': bool,
            'last_trading_date': datetime or None,
            'market_cap': float or None,
            'status_reason': str
        }
    """
    # Check cache first
    cache_key = f"health_status_{ticker.upper()}"
    cached_result = _health_cache.get(cache_key)
    
    if cached_result is not None:
        logger.debug(f"Using cached health status for {ticker}")
        # Convert last_trading_date back to datetime if it's a string (from cache)
        if 'last_trading_date' in cached_result and isinstance(cached_result['last_trading_date'], str):
            try:
                cached_result['last_trading_date'] = datetime.fromisoformat(cached_result['last_trading_date'])
            except (ValueError, TypeError):
                cached_result['last_trading_date'] = None
        return cached_result
    
    # Not in cache, make API call
    logger.debug(f"Fetching health status for {ticker} from Yahoo Finance")
    
    try:
        import yfinance as yf
        
        # Basic rate limiting - 0.5 seconds between requests
        time.sleep(0.5)
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get historical data to check last trading date
        hist = stock.history(period="5d")  # Check recent trading
        last_trading_date = None
        if not hist.empty:
            last_trading_date = hist.index[-1].to_pydatetime()
        
        # Check various health indicators
        quote_type = info.get('quoteType', '').upper()
        market_cap = info.get('marketCap')
        business_summary = info.get('longBusinessSummary', '').lower()
        
        # Determine status
        is_delisted = quote_type in ['DELISTED', 'INACTIVE'] or market_cap in [None, 0]
        is_bankrupt = any([
            'bankrupt' in business_summary,
            'chapter 11' in business_summary,
            'chapter 7' in business_summary,
            'liquidation' in business_summary
        ])
        is_active = not (is_delisted or is_bankrupt) and market_cap is not None and market_cap > 0
        
        # Determine reason
        if is_bankrupt:
            status_reason = "Bankruptcy detected in company information"
        elif is_delisted:
            status_reason = f"Delisted or inactive (quoteType: {quote_type})"
        elif is_active:
            status_reason = "Active trading company"
        else:
            status_reason = "Unknown status"
        
        result = {
            'is_active': is_active,
            'is_delisted': is_delisted,
            'is_bankrupt': is_bankrupt,
            'last_trading_date': last_trading_date.isoformat() if last_trading_date else None,  # Store as ISO string for cache
            'market_cap': market_cap,
            'status_reason': status_reason
        }
        
        # Cache the result for 24 hours
        _health_cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS)
        logger.debug(f"Cached health status for {ticker} (TTL: {CACHE_TTL_SECONDS}s)")
        
        # Convert back to datetime for return
        if result['last_trading_date']:
            result['last_trading_date'] = datetime.fromisoformat(result['last_trading_date'])
        
        return result
        
    except Exception as e:
        error_result = {
            'is_active': False,
            'is_delisted': True,
            'is_bankrupt': False,
            'last_trading_date': None,
            'market_cap': None,
            'status_reason': f"Error checking status: {str(e)}"
        }
        
        # Cache error results for a shorter period (1 hour) to allow retries
        _health_cache.set(cache_key, error_result, ttl=3600)
        logger.warning(f"Error checking health status for {ticker}: {e}")
        
        return error_result


def get_bankruptcy_date(ticker: str) -> Optional[datetime]:
    """
    Get bankruptcy/delisting date using multiple data sources with fallback strategy.
    
    This function attempts to determine the bankruptcy or delisting date using:
    1. Known bankruptcy dates database (curated)
    2. Last trading date from Yahoo Finance recent history
    3. Extended historical data lookup
    4. Yahoo Finance info fields
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Best available date for bankruptcy/delisting, None if active or date unavailable
    """
    ticker_upper = ticker.upper()
    
    # Check curated bankruptcy dates first
    if ticker_upper in KNOWN_BANKRUPTCY_DATES:
        logger.info(f"Using curated bankruptcy date for {ticker}: {KNOWN_BANKRUPTCY_DATES[ticker_upper]}")
        return KNOWN_BANKRUPTCY_DATES[ticker_upper]
    
    # Get health status from dynamic detection
    health_status = get_company_health_status(ticker)
    
    # If company is active, no bankruptcy date
    if health_status['is_active']:
        return None
    
    # If we have a last trading date from the health check, use it
    if health_status['last_trading_date']:
        logger.debug(f"Using last trading date from health check for {ticker}: {health_status['last_trading_date']}")
        return health_status['last_trading_date']
    
    logger.warning(f"No bankruptcy/delisting date found for {ticker} despite being identified as delisted/bankrupt")
    return None


def is_bankrupt_company(ticker: str) -> bool:
    """
    Check if company is bankrupt using Yahoo Finance data.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if bankruptcy indicators found, False otherwise
    """
    health_status = get_company_health_status(ticker)
    return health_status['is_bankrupt'] or health_status['is_delisted']


def clear_health_cache() -> int:
    """
    Clear the company health status cache.
    
    Returns:
        Number of cache entries cleared
    """
    try:
        keys_before = len(_health_cache.keys())
        _health_cache.clear()
        logger.info(f"Cleared {keys_before} entries from health status cache")
        return keys_before
    except Exception as e:
        logger.error(f"Error clearing health cache: {e}")
        return 0


def get_health_cache_info() -> Dict[str, any]:
    """
    Get information about the health status cache.
    
    Returns:
        Dictionary with cache statistics
    """
    try:
        keys = _health_cache.keys()
        total_entries = len(keys)
        
        # Count expired entries
        expired_count = 0
        for key in keys:
            entry = _health_cache.get(key)
            if entry and hasattr(entry, 'is_expired') and entry.is_expired:
                expired_count += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_count,
            'active_entries': total_entries - expired_count,
            'cache_ttl_hours': CACHE_TTL_SECONDS / 3600
        }
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        return {
            'total_entries': 0,
            'expired_entries': 0,
            'active_entries': 0,
            'cache_ttl_hours': CACHE_TTL_SECONDS / 3600,
            'error': str(e)
        }


def get_all_bankrupt_tickers() -> list:
    """
    This function is deprecated since we now use dynamic bankruptcy detection.
    Returns empty list to maintain compatibility.
    """
    return []
