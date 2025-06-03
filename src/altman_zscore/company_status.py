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
from altman_zscore.company_status_helpers import (
    detect_company_region,
    handle_special_status,
    check_company_status,
)

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
