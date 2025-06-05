"""
Helpers for company_status.py: region detection, special status handling, and related utilities.
"""

import os
import json
import logging
from datetime import date
from typing import Dict, Optional, TYPE_CHECKING

import requests
import yfinance as yf

if TYPE_CHECKING:
    from altman_zscore.company_status import CompanyStatus

logger = logging.getLogger(__name__)

# Known bankrupt companies with dates (YYYY-MM-DD)
KNOWN_BANKRUPTCIES = {
    "BIG": "2024-04-24",  # Big Lots
    "SEARS": "2018-10-15",  # Sears Holdings
    "SHLDQ": "2018-10-15",  # Sears Holdings (OTC ticker)
    "LEHMAN": "2008-09-15",  # Lehman Brothers
    "LEHMQ": "2008-09-15",  # Lehman Brothers (OTC ticker)
    "FTX": "2022-11-11",  # FTX Trading
    "TUP": "2023-07-20",  # Tupperware filed Chapter 11
    "WLMRT": "2002-07-21",  # WorldCom/MCI
    "ENRON": "2001-12-02",  # Enron
    "BLOCKBUSTER": "2010-09-23",  # Blockbuster
    "BBBY": "2023-04-23",  # Bed Bath & Beyond
    "HTZ": "2020-05-22",  # Hertz (they've since emerged)
    "GTXMQ": "2009-06-01",  # General Motors (old ticker before restructuring)
    "HMHC": "2012-07-19",  # Houghton Mifflin Harcourt
    "MTLQQ": "2020-07-28",  # Metaldyne Performance Group
    "RJETQ": "2016-07-07",  # Republic Airways
    "TWTRQ": "2013-10-04",  # Tweeter Home Entertainment (not Twitter)
}

BANKRUPTCY_INDICATORS = [
    "bankruptcy",
    "chapter 11",
    "chapter 7",
    "liquidation",
    "restructuring",
    "insolvency",
    "bankrupt",
    "receivership",
    "filing for protection",
    "debt restructuring",
]

from altman_zscore.computation.constants import (
    ERROR_MSG_TICKER_NOT_FOUND,
    ERROR_MSG_SYMBOL_NOT_FOUND,
    ERROR_MSG_DELISTED,
    ERROR_MSG_NO_TRADING,
    ERROR_MSG_KNOWN_BANKRUPTCY,
    ERROR_MSG_COMPANY_NOT_FOUND_SEC,
    ERROR_MSG_ERROR_RETRIEVING,
    ERROR_MSG_STATUS_CHECK_FAILED,
)

def detect_company_region(info: dict) -> str:
    """
    Attempt to detect the country/region of a company from Yahoo/SEC info dict.
    Returns a region string (e.g., 'US', 'EM', 'EU', 'ASIA', etc.) or 'Unknown'.
    """
    if not info:
        return "Unknown"
    country = info.get("country") or info.get("Country")
    if not country:
        return "Unknown"
    country = country.lower()
    if "united states" in country or country == "usa" or country == "us":
        return "US"
    em_countries = [
        "brazil", "india", "china", "south africa", "russia", "mexico", "indonesia", "turkey",
        "thailand", "malaysia", "philippines", "chile", "colombia", "peru", "egypt", "nigeria",
        "poland", "hungary", "czech republic",
    ]
    if any(em in country for em in em_countries):
        return "EM"
    if "germany" in country or "france" in country or "uk" in country or "europe" in country:
        return "EU"
    if "japan" in country or "china" in country or "korea" in country or "taiwan" in country:
        return "ASIA"
    return country.title()

def handle_special_status(status) -> bool:
    """
    Handle cases where a company has a special status (doesn't exist, delisted, bankrupt).
    Creates appropriate marker files and error outputs.
    Args:
        status: CompanyStatus object with the company's status information
    Returns:
        bool: True if processing should stop (special case detected), False if analysis should continue
    """
    from altman_zscore.utils.paths import get_output_dir, write_ticker_not_available
    from altman_zscore.utils.io import save_dataframe
    if status.exists and status.is_active and not status.is_bankrupt and not status.is_delisted:
        return False
    ticker = status.ticker
    message = status.get_status_message()
    reason = status.status_reason or ERROR_MSG_STATUS_CHECK_FAILED
    print(message, reason)
    write_ticker_not_available(ticker, reason=message)
    out_base = os.path.join(get_output_dir(None, ticker=ticker), f"zscore_{ticker}")
    error_result = [
        {
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": message,
            "diagnostic": reason,
            "model": "original",
            "api_payload": None,
            "status_info": status.to_dict(),
        }
    ]
    print(f"DEBUG: About to write error_result files to {out_base}_error.csv/json")
    try:
        import pandas as pd
        df = pd.DataFrame(error_result)
        save_dataframe(df, f"{out_base}_error.csv", fmt="csv")
        save_dataframe(df, f"{out_base}_error.json", fmt="json")
        logger.info(f"Status error output saved to {out_base}_error.csv and {out_base}_error.json")
        print(f"DEBUG: Wrote error_result files to {out_base}_error.csv/json")
    except Exception as e:
        print(f"DEBUG: Could not save error output: {e}")
        logger.error(f"Could not save error output: {e}")
    print(f"DEBUG: About to write status.json to {get_output_dir(None, ticker=ticker)}/status.json")
    try:
        with open(f"{get_output_dir(None, ticker=ticker)}/status.json", "w") as f:
            json.dump(status.to_dict(), f, indent=2)
        print(f"DEBUG: Wrote status.json to {get_output_dir(None, ticker=ticker)}/status.json")
    except Exception as e:
        print(f"DEBUG: Could not save status.json: {e}")
        logger.error(f"Could not save status.json: {e}")
    logger.warning(f"{message} {reason}")
    return True

def check_company_status(ticker: str, CompanyStatusClass=None) -> 'CompanyStatus':
    """
    Check if a company exists, is still listed, or has filed for bankruptcy.
    Uses multiple methods to detect special situations.
    Args:
        ticker: The ticker symbol to check
        CompanyStatusClass: The CompanyStatus class to instantiate (for circular import avoidance)
    Returns:
        CompanyStatus object with details about the ticker
    """
    # Import here for test monkeypatching
    from altman_zscore.utils.paths import get_output_dir
    from altman_zscore.api.yahoo_helpers import fetch_yfinance_data
    if CompanyStatusClass is None:
        from altman_zscore.company_status import CompanyStatus
        CompanyStatusClass = CompanyStatus
    status = CompanyStatusClass(ticker)
    ticker_obj = None
    if ticker.upper() in KNOWN_BANKRUPTCIES:
        status.is_bankrupt = True
        status.is_active = False
        status.exists = True
        status.bankruptcy_date = KNOWN_BANKRUPTCIES[ticker.upper()]
        status.status_reason = ERROR_MSG_KNOWN_BANKRUPTCY.format(date=status.bankruptcy_date)
        logger.info(f"{ticker} identified as a known bankruptcy case")
        return status  # Return immediately for known bankruptcies
    try:
        yf_data = fetch_yfinance_data(ticker)
        if yf_data is None:
            status.exists = False
            status.is_active = False
            status.error_message = ERROR_MSG_TICKER_NOT_FOUND
            return status
        ticker_obj = yf.Ticker(ticker)  # For legacy compatibility (news, etc.)
        info = yf_data["info"]
        output_path = get_output_dir("yf_info.json", ticker=ticker)
        with open(output_path, "w") as f:
            json.dump(info, f, indent=2)
        if not info or info.get("quoteType") == "NONE":
            status.exists = False
            status.is_active = False
            status.error_message = ERROR_MSG_TICKER_NOT_FOUND
            return status
        if "symbol" not in info:
            status.exists = False
            status.is_active = False
            status.error_message = ERROR_MSG_SYMBOL_NOT_FOUND
            return status
        if info.get("quoteType") == "DELISTED":
            status.is_active = False
            status.is_delisted = True
            status.status_reason = ERROR_MSG_DELISTED
        try:
            hist = ticker_obj.history(period="1mo")
            if hist.empty:
                status.is_active = False
                status.status_reason = ERROR_MSG_NO_TRADING
            else:
                last_date = hist.index[-1]
                import pandas as pd
                # If last_date is a pandas Index, get the last value as a Timestamp
                if isinstance(last_date, pd.Index):
                    last_date = last_date.to_list()[-1]
                # If last_date is a pandas Timestamp, convert to datetime
                if isinstance(last_date, pd.Timestamp):
                    last_date_dt = last_date.to_pydatetime()
                else:
                    last_date_dt = last_date
                status.last_trading_date = last_date_dt.strftime("%Y-%m-%d") if hasattr(last_date_dt, "strftime") else str(last_date_dt)
                today = date.today()
                # If last_date_dt is datetime, get .date(), else use as is
                if hasattr(last_date_dt, "date"):
                    last_trade_date = last_date_dt.date()
                else:
                    last_trade_date = last_date_dt
                days_since_last_trade = (today - last_trade_date).days if hasattr(last_trade_date, "__sub__") else None
                if days_since_last_trade is not None and days_since_last_trade > 5:
                    status.is_active = False
                    status.status_reason = f"No trading activity for {days_since_last_trade} days"
        except Exception as e:
            logger.warning(f"Error checking history for {ticker}: {e}")
    except Exception as e:
        logger.warning(f"Error fetching Yahoo Finance info for {ticker}: {e}")
        status.error_message = ERROR_MSG_ERROR_RETRIEVING.format(error=str(e))
        if "404" in str(e):
            status.exists = False
            status.is_active = False
        return status
    if status.exists and ticker_obj is not None and hasattr(ticker_obj, "info") and ticker_obj.info:
        try:
            description = ticker_obj.info.get("longBusinessSummary", "")
            if description:
                description = description.lower()
                for indicator in BANKRUPTCY_INDICATORS:
                    if indicator in description:
                        status.is_bankrupt = True
                        status.status_reason = f"Bankruptcy indicator found in company description: '{indicator}'"
                        break
        except Exception as e:
            logger.debug(f"Error checking bankruptcy indicators for {ticker}: {e}")
        try:
            if hasattr(ticker_obj, "news"):
                news = ticker_obj.news
                if news:
                    for item in news:
                        title = item.get("title", "").lower()
                        if any(term in title for term in BANKRUPTCY_INDICATORS):
                            status.is_bankrupt = True
                            status.status_reason = f"Bankruptcy indicator found in recent news: '{title}'"
                            break
        except Exception as e:
            logger.debug(f"Error checking news for {ticker}: {e}")
    if not status.is_active and not status.is_delisted and not status.is_bankrupt:
        try:
            from altman_zscore.api.sec_client import SECClient
            sec_url = (
                f"{SECClient.BROWSE_EDGAR_URL}?CIK={ticker}&Find=Search&owner=exclude&action=getcompany"
            )
            sec_response = requests.get(sec_url, headers={"User-Agent": "Mozilla/5.0"})
            if sec_response.status_code == 404 or "No matching companies" in sec_response.text:
                status.exists = False
                status.status_reason = ERROR_MSG_COMPANY_NOT_FOUND_SEC
        except Exception as e:
            logger.warning(f"Error checking SEC status for {ticker}: {e}")
    return status
