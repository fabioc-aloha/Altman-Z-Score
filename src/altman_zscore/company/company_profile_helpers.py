"""
company_profile_helpers.py
-------------------------
Helper functions for company profile parsing, classification, and SEC/Yahoo data extraction.
Currently limited to U.S.-based companies only.

This module provides utility functions to support company profile construction and classification
for Altman Z-Score model selection.
"""

import logging
logger = logging.getLogger(__name__)

def find_field(yf_info, possible_keys):
    """
    Search for the first non-empty value among possible keys in a dictionary.

    Args:
        yf_info (dict): Dictionary (e.g., yfinance info payload).
        possible_keys (list): List of possible field names to search for.
    Returns:
        Any: The first non-empty value found, or None if none found.
    """
    for key in possible_keys:
        val = yf_info.get(key)
        if val:
            return val
    return None

def get_industry_group(industry: str):
    """
    Map an industry string to an IndustryGroup enum value.

    Args:
        industry (str): Industry string.
    Returns:
        IndustryGroup: Enum value for the industry group.
    """    # Import here to avoid circular import
    from .company_profile import IndustryGroup
    if not industry:
        return IndustryGroup.OTHER
    ind_lower = str(industry).lower()
    if "tech" in ind_lower:
        return IndustryGroup.TECH
    elif "bank" in ind_lower or "financ" in ind_lower:
        return IndustryGroup.FINANCIAL
    elif (
        "manufactur" in ind_lower
        or "consumer electronics" in ind_lower
        or "hardware" in ind_lower
        or "semiconductor" in ind_lower
    ):
        return IndustryGroup.MANUFACTURING
    elif "service" in ind_lower or "entertain" in ind_lower:
        return IndustryGroup.SERVICE
    else:
        return IndustryGroup.OTHER

def classify_maturity(founding_year, ipo_date, current_year=None):
    """
    Classify company as 'early-stage', 'growth', or 'mature' using founding year and IPO date.

    Args:
        founding_year (int or None): Year the company was founded.
        ipo_date (str or None): IPO date (YYYY-MM-DD) if available.
        current_year (int or None): Current year (optional, defaults to system year).
    Returns:
        str: Maturity classification ('early-stage', 'growth', 'mature').
    """
    import datetime
    if not current_year:
        current_year = datetime.datetime.now().year
    if ipo_date:
        try:
            ipo_year = int(str(ipo_date)[:4])
            years_since_ipo = current_year - ipo_year
            if years_since_ipo < 3:
                return "early-stage"
            elif years_since_ipo < 7:
                return "growth"
            else:
                return "mature"
        except Exception:
            pass
    if founding_year:
        try:
            years_since_founding = current_year - int(founding_year)
            if years_since_founding < 3:
                return "early-stage"
            elif years_since_founding < 7:
                return "growth"
            else:
                return "mature"
        except Exception:
            pass
    return "mature"  # Default fallback
