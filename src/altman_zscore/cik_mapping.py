"""Stock ticker to CIK mapping configuration."""
from typing import Dict
import logging
from .cik_lookup import lookup_cik

logger = logging.getLogger(__name__)

def get_cik_mapping(tickers: list[str]) -> Dict[str, str]:
    """
    Get CIK mappings for a list of tickers.
    
    Args:
        tickers (list[str]): List of stock tickers
        
    Returns:
        Dict[str, str]: Dictionary mapping tickers to CIKs
    """
    cik_map = {}
    for ticker in tickers:
        try:
            cik = lookup_cik(ticker)
            if cik:
                cik_map[ticker] = cik
            else:
                logger.warning(f"Could not find CIK for {ticker}")
        except Exception as e:
            logger.error(f"Error looking up CIK for {ticker}: {e}")
    
    return cik_map
