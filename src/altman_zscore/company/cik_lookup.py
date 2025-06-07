"""
cik_lookup.py
-------------
Module for looking up CIK numbers from SEC EDGAR.

This module provides functionality to look up Central Index Key (CIK) numbers for companies
using their stock ticker symbols. It includes both synchronous and asynchronous lookup
capabilities, caching mechanism with TTL, and batch processing support.

Features:
    - Single and batch CIK lookups
    - Async support for improved performance
    - Local caching with TTL
    - Fallback mechanisms and retry logic
    - Rate limiting for SEC EDGAR compliance
    - Portfolio validation utilities

Functions:
    lookup_cik(ticker): Look up CIK number for a ticker symbol.
    validate_cik(ticker, expected_cik): Validate a CIK number matches what we expect from SEC.
    validate_portfolio_ciks(portfolio): Validate CIKs for all tickers in a portfolio.
"""

import logging
from typing import Dict, Optional

from .api.sec_client import SECClient

logger = logging.getLogger(__name__)


def lookup_cik(ticker: str) -> Optional[str]:
    """
    Look up CIK number for a ticker symbol using the SECClient.

    Args:
        ticker (str): Stock ticker symbol.
    Returns:
        str or None: 10-digit CIK if found, else None.
    """
    try:
        client = SECClient()
        return client.lookup_cik(ticker)
    except Exception as e:
        logger.error(f"Failed to look up CIK for {ticker}: {str(e)}")
        return None


def validate_cik(ticker: str, expected_cik: str) -> bool:
    """
    Validate a CIK number matches what we expect from SEC.

    Args:
        ticker (str): Stock ticker symbol.
        expected_cik (str): Expected 10-digit CIK string.
    Returns:
        bool: True if the found CIK matches the expected CIK, False otherwise.
    """
    try:
        client = SECClient()
        found_cik = client.lookup_cik(ticker)
        return found_cik == expected_cik
    except Exception as e:
        logger.error(f"Failed to validate CIK for {ticker}: {str(e)}")
        return False


def validate_portfolio_ciks(portfolio: Dict[str, str]) -> Dict[str, bool]:
    """
    Validate CIKs for all tickers in a portfolio.

    Args:
        portfolio (dict): Mapping of ticker symbols to expected CIKs.
    Returns:
        dict: Mapping of ticker symbols to validation results (True/False).
    """
    results = {}
    client = SECClient()
    for ticker, expected_cik in portfolio.items():
        try:
            found_cik = client.lookup_cik(ticker)
            results[ticker] = found_cik == expected_cik
        except Exception as e:
            logger.error(f"Failed to validate CIK for {ticker}: {str(e)}")
            results[ticker] = False
    return results
