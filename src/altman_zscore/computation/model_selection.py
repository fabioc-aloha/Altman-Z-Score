"""
Model selection logic for Altman Z-Score analysis.
Currently limited to U.S.-based companies only.

Provides functions to select the appropriate Z-Score model key based on SIC code and company type.
"""

from typing import Optional, Dict
from .constants import MODEL_COEFFICIENTS, MODEL_ALIASES


def is_tech_company(sic_code: Optional[int]) -> bool:
    """Determine if a company is in the technology sector based on SIC code."""
    if not isinstance(sic_code, int):
        return False
        
    return (
        (3570 <= sic_code <= 3579)  # Computer Equipment
        or (3670 <= sic_code <= 3679)  # Electronics
        or (7370 <= sic_code <= 7379)  # Computer Services/Software
    )


def is_finance_or_insurance_company(sic_code: Optional[int]) -> bool:
    """Return True if SIC code is in the finance/insurance range (6000–6999)."""
    return isinstance(sic_code, int) and 6000 <= sic_code <= 6999


def get_model_selection_context(
    sic_code: Optional[int],
    is_public: bool,
    selected_model: str
) -> Dict:
    """Get the context for model selection."""
    context = {
        "original_sic": sic_code,
        "is_public": is_public,
        "selection_reason": [],
        "selected_model": selected_model
    }

    if isinstance(sic_code, int):
        sic_key = f"sic_{sic_code}"
        if sic_key in MODEL_COEFFICIENTS:
            context["selection_reason"].append(f"Found specific model for SIC {sic_code}")
        elif is_tech_company(sic_code):
            context["selection_reason"].append(
                f"Technology company (SIC {sic_code}) using {'public' if is_public else 'private'} service model"
            )
        elif 2000 <= sic_code <= 3999:
            context["selection_reason"].append(
                f"Manufacturing company (SIC {sic_code}) using {'public' if is_public else 'private'} model"
            )
        elif (4000 <= sic_code <= 4999 or 7000 <= sic_code <= 8999):
            context["selection_reason"].append(
                f"Service/non-manufacturing company (SIC {sic_code}) using {'public' if is_public else 'private'} service model"
            )
    else:
        context["selection_reason"].append(
            f"Using default {'public' if is_public else 'private'} model (no specific industry match)"
        )
    
    return context


def select_zscore_model(
    sic_code: Optional[int],
    is_public: bool = True
) -> Optional[str]:
    """Select and return one of the canonical Altman Z-Score model keys, or None for unsupported sectors.
    Currently limited to U.S.-based companies only.

    Args:
        sic_code (int, optional): SIC code for the company.
        is_public (bool, optional): Whether the company is public (default: True).

    Returns:
        str: Canonical model key for use in computation
    """
    # 0) Finance/Insurance: not supported
    if is_finance_or_insurance_company(sic_code):
        import logging
        logging.getLogger(__name__).warning(
            f"SIC {sic_code} is finance/insurance. Altman Z-Score is not valid for this sector. Skipping analysis."
        )
        return None

    # 1) Check for explicit SIC override entry
    if isinstance(sic_code, int):
        sic_key = f"sic_{sic_code}"
        if sic_key in MODEL_COEFFICIENTS:
            return sic_key
    # 2) Retail company check (SIC 5200–5999)
    if isinstance(sic_code, int) and 5200 <= sic_code <= 5999:
        return "retail"
    # 3) Tech company check
    if is_tech_company(sic_code):
        return "em" if is_public else "private"
    # 4) Manufacturing (SIC 2000–3999)
    if isinstance(sic_code, int) and 2000 <= sic_code <= 3999:
        return "original" if is_public else "private"
    # 5) Non-manufacturing / Service / Transport / Utilities
    if isinstance(sic_code, int) and (
        4000 <= sic_code <= 4999   # Transport / Service / Utilities
        or 7000 <= sic_code <= 8999  # Services / Retail
    ):
        return "em" if is_public else "private"
    # 6) Default fallback
    return "original" if is_public else "private"


def canonicalize_model_key(key: str) -> str:
    """Return the canonical model key for a given alias or legacy key.

    Args:
        key (str): Potentially legacy or aliased model key.

    Returns:
        str: Canonical model key.
    """
    return MODEL_ALIASES.get(key, key)


def determine_zscore_model(profile) -> Optional[str]:
    """Select Z-Score model based on company profile attributes. Returns None for unsupported sectors.

    Args:
        profile: Company profile object with attributes 'sic_code' or 'sic' and 'is_public'.

    Returns:
        str: Canonical model key for use in computation.
    """
    # Check for both 'sic_code' and 'sic' attributes
    sic_code = getattr(profile, 'sic_code', None) or getattr(profile, 'sic', None)
    is_public = getattr(profile, 'is_public', True)
    
    # Convert string SIC to int if needed
    if isinstance(sic_code, str) and sic_code.isdigit():
        sic_code = int(sic_code)
    elif not isinstance(sic_code, int):
        sic_code = None
        
    return select_zscore_model(sic_code, is_public)


def select_zscore_model_by_sic(sic_code: str, is_public: bool = True) -> str:
    """Select Z-Score model based on SIC code string.

    Args:
        sic_code (str): SIC code as a string.
        is_public (bool, optional): Whether the company is public (default: True).

    Returns:
        str: Canonical model key for use in computation.
    """
    # Convert string SIC to int if possible
    if sic_code and sic_code.isdigit():
        sic_int = int(sic_code)
    else:
        sic_int = None
    
    return select_zscore_model(sic_int, is_public)
