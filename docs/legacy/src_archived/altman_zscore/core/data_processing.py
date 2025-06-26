"""
Context preparation and data processing for Altman Z-Score analysis.

This module provides helpers for preparing context information, extracting SIC codes, and filtering valid financial quarters. All functions are designed for modular use in the analysis pipeline and robust error handling.
"""

from datetime import datetime
from altman_zscore.company.sic_lookup import sic_map
from altman_zscore.plotting.terminal import print_warning

def prepare_context_info(ticker: str, profile, model) -> dict:
    """
    Prepare a context info dictionary for reporting and LLM analysis.
    Args:
        ticker: Stock ticker symbol.
        profile: Company profile object or dictionary from Yahoo Finance.
        model: Z-Score model instance.
    Returns:
        Dictionary with context fields for reporting.
    """
    # Extract SIC code from profile if available
    industry = getattr(profile, "industry", "Unknown") if not isinstance(profile, dict) else profile.get("industry", "Unknown")
    sic_code = extract_sic_code_from_industry(industry)
    is_public = getattr(profile, "is_public", "Unknown") if not isinstance(profile, dict) else profile.get("is_public", "Unknown")
    maturity = getattr(profile, "maturity", None) if not isinstance(profile, dict) else profile.get("maturity", None)
    
    maturity_map = {
        "early": "Early Stage",
        "growth": "Growth Stage",
        "mature": "Mature Company",
        "private": "Private Company",
        "public": "Public Company",
    }

    sic_desc = sic_map.get(str(sic_code)) if sic_code else None
    if sic_desc:
        industry_for_context = sic_desc
    elif sic_code:
        industry_for_context = f"SIC {sic_code}"
    else:
        industry_for_context = industry    # Explicit type handling for is_public and maturity
    maturity_str = maturity.lower() if isinstance(maturity, str) else str(maturity).lower() if maturity is not None else None
    is_public_str = is_public.lower() if isinstance(is_public, str) else str(is_public).lower() if is_public is not None else "unknown"

    # Extract readable model name from model object
    model_name = "Unknown"
    if hasattr(model, 'model_type'):
        model_name = model.model_type.value.title() + " Z-Score Model"
    elif hasattr(model, '__class__'):
        class_name = model.__class__.__name__
        if "Original" in class_name:
            model_name = "Original Altman Z-Score Model"
        elif "Private" in class_name:
            model_name = "Z'-Score (Private Company) Model"
        elif "Financial" in class_name:
            model_name = "Financial Institution Z-Score Model"
        # Removed deprecated ZETA model conversion
        elif "Retail" in class_name:
            model_name = "Retail Industry Z-Score Model"
        else:
            model_name = class_name.replace("ZScoreModel", "").replace("Model", "") + " Model"

    return {
        "Ticker": ticker,
        "Industry": industry_for_context,
        "Public": is_public,
        "Maturity": (
            maturity_map.get(maturity_str, "Mature Company")
            if maturity_str
            else ("Mature Company" if is_public_str == "true" else "Unknown")
        ),
        "Model": model_name,
        "Model_Type": model.model_type.value if hasattr(model, 'model_type') else "unknown",
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

def filter_quarters_by_start_date_and_fields(quarters_dict, start_date=None, required_fields=None):
    """
    Filter a dict of quarterly data to only include quarters on or after start_date 
    and only the required fields.

    Args:
        quarters_dict: Dict mapping period_end to dict of fields (e.g., {"2024-03-31": {...}})
        start_date: Optional, only include quarters on or after this date (YYYY-MM-DD)
        required_fields: Optional, list of fields to keep in each quarter (if None, keep all)
    Returns:
        Filtered dict of quarters, sorted by period_end ascending.
    """
    if not isinstance(quarters_dict, dict):
        return {}
    filtered = {}
    for period, data in quarters_dict.items():
        try:
            period_dt = datetime.strptime(str(period)[:10], "%Y-%m-%d").date()
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                if period_dt < start_dt:
                    continue
            if required_fields:
                filtered[period] = {k: v for k, v in data.items() if k in required_fields}
            else:
                filtered[period] = dict(data)
        except Exception:
            continue
    # Sort by period_end ascending
    return dict(sorted(filtered.items(), key=lambda x: x[0]))
