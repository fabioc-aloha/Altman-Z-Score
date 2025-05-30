"""
Enhancements to the bankruptcy and delisting detection for Altman Z-Score tool.

This module provides additional checks to detect bankruptcies, delistings, and other
special situations more gracefully before attempting full financial analysis.
"""

import json
import logging
import os
from datetime import date
from typing import Dict, Optional

import requests
import yfinance as yf

from altman_zscore.utils.paths import get_output_dir, write_ticker_not_available

logger = logging.getLogger(__name__)

# Known bankrupt companies with dates (YYYY-MM-DD)
KNOWN_BANKRUPTCIES = {
    "BIG": "2024-04-24",  # Big Lots
    "SEARS": "2018-10-15",  # Sears Holdings
    "SHLDQ": "2018-10-15",  # Sears Holdings (OTC ticker)
    "LEHMAN": "2008-09-15",  # Lehman Brothers
    "LEHMQ": "2008-09-15",  # Lehman Brothers (OTC ticker)
    "FTX": "2022-11-11",  # FTX Trading
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

# Common bankruptcy-related terms
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


class CompanyStatus:
    """
    Class representing the current status of a company/ticker.
    """

    def __init__(
        self,
        ticker: str,
        exists: bool = True,
        is_active: bool = True,
        is_bankrupt: bool = False,
        is_delisted: bool = False,
        last_trading_date: Optional[str] = None,
        error_message: Optional[str] = None,
        bankruptcy_date: Optional[str] = None,
        status_reason: Optional[str] = None,
    ):
        self.ticker = ticker
        self.exists = exists  # If ticker exists at all
        self.is_active = is_active  # If ticker is currently tradeable
        self.is_bankrupt = is_bankrupt  # If company has filed for bankruptcy
        self.is_delisted = is_delisted  # If ticker has been delisted
        self.last_trading_date = last_trading_date
        self.error_message = error_message
        self.bankruptcy_date = bankruptcy_date
        self.status_reason = status_reason

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "ticker": self.ticker,
            "exists": self.exists,
            "is_active": self.is_active,
            "is_bankrupt": self.is_bankrupt,
            "is_delisted": self.is_delisted,
            "last_trading_date": self.last_trading_date,
            "error_message": self.error_message,
            "bankruptcy_date": self.bankruptcy_date,
            "status_reason": self.status_reason,
        }

    def get_status_message(self) -> str:
        """Generate a user-friendly status message."""
        # Bankruptcy is highest priority status since it's most important to know
        if self.is_bankrupt:
            bankruptcy_info = f" (filed on {self.bankruptcy_date})" if self.bankruptcy_date else ""
            return f"{self.ticker} has filed for bankruptcy{bankruptcy_info}."

        if self.is_delisted:
            delisting_info = f" (last traded on {self.last_trading_date})" if self.last_trading_date else ""
            return f"{self.ticker} has been delisted{delisting_info}."

        if not self.exists:
            return f"The ticker '{self.ticker}' does not appear to exist."

        if not self.is_active:
            return f"{self.ticker} exists but is not currently active. {self.status_reason or ''}"

        return f"{self.ticker} appears to be an active company."


def check_company_status(ticker: str) -> CompanyStatus:
    """
    Check if a company exists, is still listed, or has filed for bankruptcy.
    Uses multiple methods to detect special situations.

    Args:
        ticker: The ticker symbol to check

    Returns:
        CompanyStatus object with details about the ticker
    """
    status = CompanyStatus(ticker)
    ticker_obj = None
    # Check for known bankruptcies first (static list)
    if ticker.upper() in KNOWN_BANKRUPTCIES:
        status.is_bankrupt = True
        status.is_active = False
        status.exists = True  # The company did exist at some point
        status.bankruptcy_date = KNOWN_BANKRUPTCIES[ticker.upper()]
        status.status_reason = f"Known bankruptcy case (filed on {status.bankruptcy_date})"
        logger.info(f"{ticker} identified as a known bankruptcy case")

    # Step 1: Basic Yahoo Finance check
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info

        # Save the raw yfinance info payload for traceability
        output_path = get_output_dir("yf_info.json", ticker=ticker)
        with open(output_path, "w") as f:
            json.dump(info, f, indent=2)

        # Check if info contains meaningful data
        if not info or info.get("quoteType") == "NONE":
            status.exists = False
            status.is_active = False
            status.error_message = "Ticker not found in Yahoo Finance"
            return status

        # Check for no symbols (404 error)
        if "symbol" not in info:
            status.exists = False
            status.is_active = False
            status.error_message = "Ticker symbol not found in Yahoo Finance"
            return status

        # Check for delisting indicators in the info
        if info.get("quoteType") == "DELISTED":
            status.is_active = False
            status.is_delisted = True
            status.status_reason = "Delisted according to Yahoo Finance"

        # Check for last price date as an indicator of delisting
        try:
            hist = ticker_obj.history(period="1mo")
            if hist.empty:
                status.is_active = False
                status.status_reason = "No recent trading data available"
            else:
                last_date = hist.index[-1]
                status.last_trading_date = last_date.strftime("%Y-%m-%d")

                # If last trading date is more than 5 trading days ago, may be delisted
                # Convert to datetime.date() to avoid timezone issues
                today = date.today()
                last_trade_date = last_date.date() if hasattr(last_date, "date") else last_date
                days_since_last_trade = (today - last_trade_date).days

                if days_since_last_trade > 5:
                    status.is_active = False
                    status.status_reason = f"No trading activity for {days_since_last_trade} days"
        except Exception as e:
            logger.warning(f"Error checking history for {ticker}: {e}")

    except Exception as e:
        logger.warning(f"Error fetching Yahoo Finance info for {ticker}: {e}")
        status.error_message = f"Error retrieving data: {str(e)}"
        # For 404 errors, mark as non-existent
        if "404" in str(e):
            status.exists = False
            status.is_active = False
        # If we hit an error fetching info, do not proceed to further checks
        return status

    # Only check description and news if ticker exists and info is valid
    if status.exists and ticker_obj is not None and hasattr(ticker_obj, "info") and ticker_obj.info:
        # Step 2: Check for bankruptcy indicators in company description or news
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
        # Step 3: Try to get recent news to detect bankruptcy filings
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

    # If the ticker is inactive and we've found no specific reason, try to check SEC status
    if not status.is_active and not status.is_delisted and not status.is_bankrupt:
        try:
            # Check SEC Edgar company search (just a basic check if it returns a 404)
            sec_url = (
                f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&Find=Search&owner=exclude&action=getcompany"
            )
            sec_response = requests.get(sec_url, headers={"User-Agent": "Mozilla/5.0"})

            if sec_response.status_code == 404 or "No matching companies" in sec_response.text:
                status.exists = False
                status.status_reason = "Company not found in SEC EDGAR database"
        except Exception as e:
            logger.warning(f"Error checking SEC status for {ticker}: {e}")

    return status


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
    # Example EM/region logic (expand as needed)
    em_countries = [
        "brazil",
        "india",
        "china",
        "south africa",
        "russia",
        "mexico",
        "indonesia",
        "turkey",
        "thailand",
        "malaysia",
        "philippines",
        "chile",
        "colombia",
        "peru",
        "egypt",
        "nigeria",
        "poland",
        "hungary",
        "czech republic",
    ]
    if any(em in country for em in em_countries):
        return "EM"
    # Add more region logic as needed
    if "germany" in country or "france" in country or "uk" in country or "europe" in country:
        return "EU"
    if "japan" in country or "china" in country or "korea" in country or "taiwan" in country:
        return "ASIA"
    return country.title()


def handle_special_status(status: CompanyStatus) -> bool:
    """
    Handle cases where a company has a special status (doesn't exist, delisted, bankrupt).
    Creates appropriate marker files and error outputs.

    Args:
        status: CompanyStatus object with the company's status information

    Returns:
        bool: True if processing should stop (special case detected), False if analysis should continue
    """
    if status.exists and status.is_active and not status.is_bankrupt and not status.is_delisted:
        # Company appears normal, continue with analysis
        return False

    ticker = status.ticker
    message = status.get_status_message()
    reason = status.status_reason or "Company status check failed"

    # Print status message to terminal
    print(message, reason)

    # Create TICKER_NOT_AVAILABLE.txt with detailed reason
    write_ticker_not_available(ticker, reason=message)

    # Create error JSON/CSV with more detailed information
    out_base = os.path.join(get_output_dir(None, ticker=ticker), f"zscore_{ticker}")

    error_result = [
        {
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": message,
            "diagnostic": reason,
            "model": "original",  # Default model since we don't have financial data
            "api_payload": None,
            # Additional status information
            "status_info": status.to_dict(),
        }
    ]

    try:
        import pandas as pd

        df = pd.DataFrame(error_result)
        df.to_csv(f"{out_base}_error.csv", index=False)
        df.to_json(f"{out_base}_error.json", orient="records", indent=2)
        logger.info(f"Status error output saved to {out_base}_error.csv and {out_base}_error.json")
    except Exception as e:
        logger.error(f"Could not save error output: {e}")

    # Create a status.json file with detailed status information
    try:
        with open(f"{get_output_dir(None, ticker=ticker)}/status.json", "w") as f:
            json.dump(status.to_dict(), f, indent=2)
    except Exception as e:
        logger.error(f"Could not save status.json: {e}")

    # Log the issue
    logger.warning(f"{message} {reason}")

    return True  # Signal that processing should stop
