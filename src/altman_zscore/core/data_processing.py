"""
Context preparation and data processing for Altman Z-Score analysis.

This module provides helpers for preparing context information, extracting SIC codes, and filtering valid financial quarters. All functions are designed for modular use in the analysis pipeline and robust error handling.
"""

from datetime import datetime
import pandas as pd
from altman_zscore.company.sic_lookup import sic_map
from altman_zscore.plotting.terminal import print_warning

def prepare_context_info(ticker: str, profile, model: str, sic_code: str) -> dict:
    """
    Prepare a context info dictionary for reporting and LLM analysis.
    Args:
        ticker: Stock ticker symbol.
        profile: Company profile object (should have industry, is_public, is_emerging_market, maturity attributes).
        model: Z-Score model name.
        sic_code: SIC code string.
    Returns:
        Dictionary with context fields for reporting.
    """
    industry = getattr(profile, "industry", "Unknown")
    is_public = getattr(profile, "is_public", "Unknown")
    is_em = getattr(profile, "is_emerging_market", "Unknown")
    maturity = getattr(profile, "maturity", None)
    
    maturity_map = {
        "early": "Early Stage",
        "growth": "Growth Stage",
        "mature": "Mature Company",
        "emerging": "Emerging Market",
        "private": "Private Company",
        "public": "Public Company",
    }

    sic_desc = sic_map.get(str(sic_code)) if sic_code else None
    if sic_desc:
        industry_for_context = sic_desc
    elif sic_code:
        industry_for_context = f"SIC {sic_code}"
    else:
        industry_for_context = industry

    # Explicit type handling for is_public and maturity
    maturity_str = maturity.lower() if isinstance(maturity, str) else str(maturity).lower() if maturity is not None else None
    is_public_str = is_public.lower() if isinstance(is_public, str) else str(is_public).lower() if is_public is not None else "unknown"

    return {
        "Ticker": ticker,
        "Industry": industry_for_context,
        "Public": is_public,
        "Emerging Market": is_em,
        "Maturity": (
            maturity_map.get(maturity_str, "Mature Company")
            if maturity_str
            else ("Mature Company" if is_public_str == "true" else "Unknown")
        ),
        "Model": model,
        "SIC Code": sic_code or "N/A",
        "Analysis Date": datetime.now().strftime("%Y-%m-%d"),
    }

def extract_sic_code_from_industry(industry: str) -> str | None:
    """
    Extract SIC code from an industry string if present and valid.

    Only returns a code if the word 'SIC' is followed by all digits.

    Args:
        industry: Industry string (may contain 'SIC <digits>').
    Returns:
        SIC code as string if found, else None.
    """
    if industry and "SIC" in str(industry):
        parts = str(industry).split()
        for i, p in enumerate(parts):
            if p == "SIC" and i + 1 < len(parts):
                code = parts[i + 1]
                if code.isdigit():
                    return code
    return None

def filter_valid_quarters(fin_info: dict, start_date: str) -> list:
    """
    Filter valid quarters based on financial info and start date.

    Args:
        fin_info: Dictionary with a 'quarters' key containing a list of quarter dicts.
        start_date: Start date in 'YYYY-MM-DD' format. Only quarters ending on or after this date are included.
    Returns:
        List of valid quarter dicts.
    Notes:
        - If the input structure is invalid, returns an empty list and logs a warning.
        - If a quarter is missing 'period_end' or it is malformed, that quarter is skipped silently.
    """
    # Validate input structure
    if not isinstance(fin_info, dict) or "quarters" not in fin_info or not isinstance(fin_info["quarters"], list):
        print_warning("Invalid financial info structure: expected dict with 'quarters' list.")
        return []
    valid_quarters = [
        q for q in fin_info["quarters"]
        if any(v not in (None, "", 0.0) for k, v in q.items() if k != "raw_payload")
    ]
    if start_date:
        start_dt = None
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        except (ValueError, TypeError) as e:
            print_warning(f"Invalid start_date format: {e}")
            return valid_quarters
        filtered = []
        for q in valid_quarters:
            try:
                if "period_end" in q and q["period_end"]:
                    period_dt = datetime.strptime(str(q["period_end"])[:10], "%Y-%m-%d").date()
                    if period_dt >= start_dt:
                        filtered.append(q)
            except (ValueError, TypeError):
                # Skip malformed dates silently
                continue
        valid_quarters = filtered
    return valid_quarters
