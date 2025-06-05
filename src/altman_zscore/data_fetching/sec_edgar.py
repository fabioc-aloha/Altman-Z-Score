"""
SEC EDGAR/XBRL data fetching and parsing utilities for financials module refactor.
"""
import logging
from typing import Any, Dict, Optional

def find_xbrl_tag(soup, tag_names):
    """Find XBRL tag value from a list of possible tag names."""
    for name in tag_names:
        tag = soup.find(name.replace(":", "_"))
        if tag:
            try:
                return float(tag.text)
            except (ValueError, TypeError):
                continue
    return None

def fetch_sec_edgar_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch company information from SEC EDGAR for the given ticker.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        dict or None: Company information if available, else None.
    """
    try:
        from altman_zscore.api.sec_client import SECClient
        client = SECClient()
        company_data = client.get_company_info(ticker, save_to_file=True)
        if company_data is None:
            return None
        return company_data
    except Exception as e:
        logging.warning(f"Failed to fetch SEC EDGAR data for {ticker}: {e}")
        return None
