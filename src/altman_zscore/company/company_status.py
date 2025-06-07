"""
company_status.py
----------------
Enhancements to the bankruptcy and delisting detection for Altman Z-Score tool.

This module provides additional checks to detect bankruptcies, delistings, and other
special situations more gracefully before attempting full financial analysis. It defines
the CompanyStatus class and related helpers for robust status reporting and user feedback.
"""

import json
import logging
import os
from datetime import date
from typing import Dict, Optional

import requests
import yfinance as yf

from altman_zscore.utils.paths import get_output_dir, write_ticker_not_available
from altman_zscore.company.company_status_helpers import (
    detect_company_region,
    handle_special_status,
    check_company_status,
    KNOWN_BANKRUPTCIES,
    BANKRUPTCY_INDICATORS,
)
from altman_zscore.computation.constants import (
    STATUS_MSG_BANKRUPT,
    STATUS_MSG_DELISTED,
    STATUS_MSG_NOT_FOUND,
    STATUS_MSG_INACTIVE,
    STATUS_MSG_ACTIVE,
)

logger = logging.getLogger(__name__)


class CompanyStatus:
    """
    Represents the current status of a company/ticker for Altman Z-Score analysis.

    Attributes:
        ticker (str): Stock ticker symbol.
        exists (bool): True if ticker exists at all.
        is_active (bool): True if ticker is currently tradeable.
        is_bankrupt (bool): True if company has filed for bankruptcy.
        is_delisted (bool): True if ticker has been delisted.
        last_trading_date (str or None): Last trading date if delisted.
        error_message (str or None): Error message if status could not be determined.
        bankruptcy_date (str or None): Bankruptcy filing date if known.
        status_reason (str or None): Additional reason for inactive status.
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
        """
        Convert the CompanyStatus instance to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the company status.
        """
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
        """
        Generate a user-friendly status message for the company/ticker.

        Returns:
            str: Status message suitable for user display.
        """
        if self.is_bankrupt:
            bankruptcy_info = f" (filed on {self.bankruptcy_date})" if self.bankruptcy_date else ""
            return STATUS_MSG_BANKRUPT.format(ticker=self.ticker, bankruptcy_info=bankruptcy_info)
        if self.is_delisted:
            delisting_info = f" (last traded on {self.last_trading_date})" if self.last_trading_date else ""
            return STATUS_MSG_DELISTED.format(ticker=self.ticker, delisting_info=delisting_info)
        if not self.exists:
            return STATUS_MSG_NOT_FOUND.format(ticker=self.ticker)
        if not self.is_active:
            return STATUS_MSG_INACTIVE.format(ticker=self.ticker, status_reason=self.status_reason or "")
        return STATUS_MSG_ACTIVE.format(ticker=self.ticker)
