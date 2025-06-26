"""
SEC market value extraction helpers for Altman Z-Score analysis.

Provides a function to extract market value of equity from SEC facts (using shares outstanding and price, or public float if available).
"""

from typing import Optional, Dict
from datetime import date


def extract_market_value_equity_from_sec(sec_facts: Dict, period_end: str) -> Optional[float]:
    """
    Attempt to extract market value of equity for a given period from SEC facts.
    Tries (in order):
      1. Public float (EntityPublicFloat)
      2. Shares outstanding (EntityCommonStockSharesOutstanding) × closing price (if available)
    Args:
        sec_facts (dict): SEC facts as returned by SECClient.get_company_facts
        period_end (str): Period end date (YYYY-MM-DD)
    Returns:
        float or None: Market value of equity if found, else None
    """
    if not sec_facts or "facts" not in sec_facts:
        return None
    facts = sec_facts["facts"]
    # 1. Try public float
    dei = facts.get("dei", {})
    public_float = dei.get("EntityPublicFloat", {}).get("units", {}).get("USD", [])
    for entry in public_float:
        if entry.get("end", "").startswith(period_end[:7]):
            val = entry.get("val")
            if val:
                return float(val)
    # 2. Try shares outstanding × price (price not available in SEC, so skip for now)
    # Could be extended if price is available from another source
    return None
