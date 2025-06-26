"""
Centralized yfinance data fetching and validation helpers for DRY compliance.
"""
import logging
import pandas as pd
from typing import Optional, Dict, Any
import requests.exceptions
import time  # for global timer sleep

import yfinance as yf

from ..utils.retry import exponential_retry

logger = logging.getLogger(__name__)

NETWORK_EXCEPTIONS = (
    requests.exceptions.RequestException,  # All requests exceptions
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
)

# Global timer for all Yahoo API calls (shared across all fetches)
LAST_API_CALL_TIME = 0.0
MIN_API_INTERVAL = 0.25  # seconds (adjust as needed for all APIs)

def validate_credentials():
    """
    Validate Yahoo Finance usage and enforce a global minimum interval between API calls.
    Raises ValueError if basic setup is missing.
    """
    global LAST_API_CALL_TIME
    now = time.time()
    elapsed = now - LAST_API_CALL_TIME
    if elapsed < MIN_API_INTERVAL:
        sleep_time = MIN_API_INTERVAL - elapsed
        logger.debug(f"Global API timer: sleeping {sleep_time:.2f}s to avoid rapid API calls.")
        time.sleep(sleep_time)
    LAST_API_CALL_TIME = time.time()
    # No explicit credentials required for yfinance but ensure library loaded
    if not hasattr(yf, 'Ticker'):
        raise ValueError("yfinance library is not properly installed or imported.")

@exponential_retry(
    max_retries=3, 
    base_delay=1.0, 
    backoff_factor=2.0,
    exceptions=NETWORK_EXCEPTIONS
)
def fetch_yfinance_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetches and validates yfinance info, balance sheet, and income statement for a ticker.
    Returns a dict with keys: 'info', 'balance_sheet', 'income_statement', or None on error.
    
    Implements exponential backoff retry for network-related errors.
    """
    validate_credentials()  # Enforce timer before API call
    logger = logging.getLogger("altman_zscore.fetch_yfinance_data")
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        bs = yf_ticker.quarterly_balance_sheet
        is_ = yf_ticker.quarterly_financials
        # Validate DataFrames
        if not isinstance(bs, pd.DataFrame) or bs.empty:
            logger.warning(f"No balance sheet data for {ticker} from yfinance.")
            bs = pd.DataFrame()
        if not isinstance(is_, pd.DataFrame) or is_.empty:
            logger.warning(f"No income statement data for {ticker} from yfinance.")
            is_ = pd.DataFrame()
        return {"info": info, "balance_sheet": bs, "income_statement": is_}
    except requests.exceptions.HTTPError as e:
        # On 401, rethrow to trigger exponential retry
        if hasattr(e, 'response') and e.response and e.response.status_code == 401:
            logger.warning(f"Yahoo Finance HTTP 401 for {ticker}, retrying...")
            raise
        logger.error(f"HTTP error fetching yfinance data for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching yfinance data for {ticker}: {e}")
        return None

@exponential_retry(
    max_retries=3, 
    base_delay=1.0, 
    backoff_factor=2.0,
    exceptions=NETWORK_EXCEPTIONS
)
def fetch_yfinance_full(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetches yfinance info, balance sheet, income statement, and all major holders, recommendations, prices, dividends, splits.
    Fetches both quarterly and annual data for comprehensive historical coverage.
    Returns a dict with all objects or None on error.    Implements exponential backoff retry for network-related errors.
    """
    validate_credentials()  # Enforce timer before API call
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        
        # Fetch both quarterly and annual financial data
        bs_quarterly = yf_ticker.quarterly_balance_sheet
        is_quarterly = yf_ticker.quarterly_financials  
        bs_annual = yf_ticker.balance_sheet
        is_annual = yf_ticker.financials
        
        major_holders = getattr(yf_ticker, "major_holders", None)
        institutional_holders = getattr(yf_ticker, "institutional_holders", None)
        recommendations = getattr(yf_ticker, "recommendations", None)
        historical_prices = yf_ticker.history(period="max")
        dividends = getattr(yf_ticker, "dividends", None)
        splits = getattr(yf_ticker, "splits", None)
        
        return {
            "info": info,
            "balance_sheet": bs_quarterly,  # Primary choice for recent data
            "income_statement": is_quarterly,  # Primary choice for recent data
            "balance_sheet_annual": bs_annual,  # For historical coverage
            "income_statement_annual": is_annual,  # For historical coverage
            "major_holders": major_holders,
            "institutional_holders": institutional_holders,
            "recommendations": recommendations,
            "historical_prices": historical_prices,
            "dividends": dividends,
            "splits": splits,
        }
    except requests.exceptions.HTTPError as e:
        # On 401, rethrow to trigger exponential retry
        if hasattr(e, 'response') and e.response and e.response.status_code == 401:
            logger.warning(f"Yahoo Finance HTTP 401 for {ticker}, retrying full fetch...")
            raise
        logger.error(f"HTTP error fetching full yfinance data for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching full yfinance data for {ticker}: {e}")
        return None
