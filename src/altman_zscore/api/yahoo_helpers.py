"""
Centralized yfinance data fetching and validation helpers for DRY compliance.
"""
import yfinance as yf
import logging
import pandas as pd
from typing import Optional, Dict, Any

def fetch_yfinance_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetches and validates yfinance info, balance sheet, and income statement for a ticker.
    Returns a dict with keys: 'info', 'balance_sheet', 'income_statement', or None on error.
    """
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
    except Exception as e:
        logger.error(f"Error fetching yfinance data for {ticker}: {e}")
        return None

def fetch_yfinance_full(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetches yfinance info, balance sheet, income statement, and all major holders, recommendations, prices, dividends, splits.
    Returns a dict with all objects or None on error.
    """
    logger = logging.getLogger("altman_zscore.fetch_yfinance_full")
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        bs = yf_ticker.quarterly_balance_sheet
        is_ = yf_ticker.quarterly_financials
        major_holders = getattr(yf_ticker, "major_holders", None)
        institutional_holders = getattr(yf_ticker, "institutional_holders", None)
        recommendations = getattr(yf_ticker, "recommendations", None)
        historical_prices = yf_ticker.history(period="max")
        dividends = getattr(yf_ticker, "dividends", None)
        splits = getattr(yf_ticker, "splits", None)
        return {
            "info": info,
            "balance_sheet": bs,
            "income_statement": is_,
            "major_holders": major_holders,
            "institutional_holders": institutional_holders,
            "recommendations": recommendations,
            "historical_prices": historical_prices,
            "dividends": dividends,
            "splits": splits,
        }
    except Exception as e:
        logger.error(f"Error fetching full yfinance data for {ticker}: {e}")
        return None
