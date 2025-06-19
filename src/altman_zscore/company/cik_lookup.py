"""
cik_lookup.py
-------------
Module for CIK lookup functionality using the SEC cache.

This module provides functionality to look up CIK numbers from ticker symbols
using the cached SEC company tickers data, eliminating the need for hard-coded
mappings and ensuring we always have the most up-to-date information.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def lookup_cik_from_sec_cache(ticker: str) -> Optional[str]:
    """
    Look up CIK from the SEC company tickers cache.
    
    Args:
        ticker: Stock ticker symbol (case-insensitive)
        
    Returns:
        Zero-padded CIK string if found, None otherwise
    """
    if not ticker:
        return None
        
    ticker = ticker.upper().strip()
    
    # Path to SEC cache file
    cache_path = Path(__file__).parent.parent / "api" / "cache" / "sec_company_tickers_cache.json"
    
    if not cache_path.exists():
        logger.warning(f"SEC cache file not found at {cache_path}")
        return None
        
    try:
        with open(cache_path, 'r') as f:
            cache = json.load(f)
            
        # Search for ticker in cache
        for cik_id, data in cache.items():
            if data.get('ticker', '').upper() == ticker:
                cik_str = data.get('cik_str')
                if cik_str:
                    # Ensure CIK is zero-padded to 10 digits
                    return f"{int(cik_str):010d}"
                    
        logger.debug(f"Ticker {ticker} not found in SEC cache")
        return None
        
    except Exception as e:
        logger.error(f"Error reading SEC cache: {e}")
        return None

# Legacy function name for backward compatibility
def get_cik_from_common_mappings(ticker: str) -> Optional[str]:
    """
    Legacy function that now uses SEC cache instead of hard-coded mappings.
    Kept for backward compatibility.
    """
    return lookup_cik_from_sec_cache(ticker)

# For backward compatibility, provide COMMON_CIK_MAPPINGS as a property that reads from cache
class _CIKMappingsProxy:
    """Proxy class to provide backward compatibility for COMMON_CIK_MAPPINGS access."""
    
    def get(self, ticker: str, default=None):
        """Get CIK for ticker, return default if not found."""
        result = lookup_cik_from_sec_cache(ticker)
        return result if result is not None else default
        
    def __contains__(self, ticker: str):
        """Check if ticker exists in cache."""
        return lookup_cik_from_sec_cache(ticker) is not None

# Create a proxy instance for backward compatibility
COMMON_CIK_MAPPINGS = _CIKMappingsProxy()
